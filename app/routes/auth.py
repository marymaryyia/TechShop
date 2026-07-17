import os 
import random
import requests
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session
)
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message

from extensions import db, csrf, mail
from app.models import User
from app.utils import (
    safe_next, 
    t, 
    generate_confirmation_token, 
    confirm_token 
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
@csrf.exempt 
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
        
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                error = t("validation.account_suspended")
            else:
                login_user(user)
                
                if user.role in ['admin', 'super_admin']:
                    next_page = request.args.get("next")
                    if next_page and next_page.startswith("/admin"):
                        return redirect(next_page)
                    return redirect(url_for("admin.admin_dashboard"))
                    
                next_page = request.args.get("next")
                return redirect(next_page if next_page else url_for("main.index"))
        else:
            error = t("validation.invalid_credentials")
            
    return render_template("login.html", error=error)


@auth_bp.route('/logout', methods=['POST'])
@csrf.exempt
def logout():
    logout_user()     
    session.clear()   
    
    response = redirect(url_for('main.index'))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
        
    error = None
    show_verify_step = False
    email = None

    if request.method == "POST":
        step = request.form.get("step", "register")
        if step == "register":
            first_name = request.form.get("first_name", "").strip()
            last_name = request.form.get("last_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            password2 = request.form.get("password2", "")
            
            if not all([first_name, last_name, email, password]):
                error = t("validation.fill_all_fields")
            elif password != password2:
                error = t("validation.passwords_dont_match")
            else:
                existing_user = User.query.filter_by(email=email).first()
                
                # --- Brevo API კონფიგურაცია ---
                api_key = os.environ.get('BREVO_API_KEY')
                brevo_url = "https://api.brevo.com/v3/smtp/email"
                headers = {
                    "accept": "application/json",
                    "api-key": api_key,
                    "content-type": "application/json"
                }
                sender_info = {"name": "TechShop", "email": "maria.kashavanidzete07@geolab.edu.ge"}
                # ------------------------------

                if existing_user:
                    if existing_user.is_active:
                        error = t("validation.email_exists")
                        return render_template("register.html", error=error, show_verify_step=False)
                    else:
                        verification_code = str(random.randint(100000, 999999))
                        existing_user.verification_code = verification_code
                        existing_user.first_name = first_name
                        existing_user.last_name = last_name
                        existing_user.set_password(password)
                        db.session.commit()
                        
                        try:
                            # მეილის გაგზავნა Brevo-თი (უკვე არსებული, მაგრამ არააქტიური იუზერისთვის)
                            payload = {
                                "sender": sender_info,
                                "to": [{"email": existing_user.email, "name": existing_user.first_name}],
                                "subject": "ვერიფიკაციის კოდი - TechShop",
                                "htmlContent": f"<html><body><h3>გამარჯობა, {existing_user.first_name}!</h3><p>თქვენი ვერიფიკაციის კოდია: <strong style='font-size: 20px;'>{verification_code}</strong></p></body></html>"
                            }
                            resp = requests.post(brevo_url, json=payload, headers=headers)
                            if resp.status_code not in [200, 201, 202]:
                                raise Exception(f"Brevo Error: {resp.text}")
                                
                        except Exception as e:
                            print(f"\n[MAIL ERROR] ---> {e}\n")
                            error = "მეილის გაგზავნა ვერ მოხერხდა. შეამოწმეთ Brevo კონფიგურაცია და ტერმინალი!"
                            return render_template("register.html", error=error, show_verify_step=False)
                        
                        show_verify_step = True
                        return render_template("register.html", show_verify_step=show_verify_step, email=email)

                # --- ახალი მომხმარებლის რეგისტრაცია ---
                verification_code = str(random.randint(100000, 999999))
                new_user = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    role='user',
                    is_active=False,
                    verification_code=verification_code
                )
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                
                try:
                    # მეილის გაგზავნა Brevo-თი (ახალი იუზერისთვის)
                    payload = {
                        "sender": sender_info,
                        "to": [{"email": new_user.email, "name": new_user.first_name}],
                        "subject": "ვერიფიკაციის კოდი - TechShop",
                        "htmlContent": f"<html><body><h3>გამარჯობა, {new_user.first_name}!</h3><p>თქვენი ვერიფიკაციის კოდია: <strong style='font-size: 20px;'>{verification_code}</strong></p></body></html>"
                    }
                    resp = requests.post(brevo_url, json=payload, headers=headers)
                    if resp.status_code not in [200, 201, 202]:
                        raise Exception(f"Brevo Error: {resp.text}")
                        
                except Exception as e:
                    print(f"\n[MAIL ERROR] ---> {e}\n")
                    error = "მეილის გაგზავნა ვერ მოხერხდა. შეამოწმეთ Brevo კონფიგურაცია!"
                    db.session.delete(new_user)  
                    db.session.commit()
                    return render_template("register.html", error=error, show_verify_step=False)
                
                show_verify_step = True
                return render_template("register.html", show_verify_step=show_verify_step, email=email)
   
        elif step == "verify":
            email = request.form.get("email", "").strip()
            entered_code = request.form.get("code", "").strip()
            
            db_user = User.query.filter_by(email=email).first()
            
            if db_user and db_user.verification_code == entered_code:
                db_user.is_active = True
                db_user.verification_code = None
                db.session.commit()
                
                flash("გილოცავთ! თქვენი ანგარიში წარმატებით გააქტიურდა. ახლა შეგიძლიათ შეხვიდეთ სისტემაში.", "success")
                return redirect(url_for("auth.login"))
            else:
                error = "არასწორი ვერიფიკაციის კოდი. გთხოვთ, სცადოთ თავიდან."
                show_verify_step = True
                return render_template("register.html", error=error, show_verify_step=show_verify_step, email=email)

    return render_template("register.html", error=error, show_verify_step=show_verify_step)