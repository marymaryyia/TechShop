document.addEventListener('DOMContentLoaded', function () {

  /* ---------------------------------------------------------------------
   * Theme switch (light / dark) — persisted in localStorage so it survives
   * a page reload. The <html data-theme="..."> attribute drives every
   * themed CSS variable in style.css.
   * ------------------------------------------------------------------- */
  var root = document.documentElement;
  var toggleButtons = [
    document.getElementById('themeToggle'),
    document.getElementById('themeToggleMobile')
  ].filter(Boolean);

  function currentTheme() {
    return root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  }

  function updateToggleIcons() {
    var isDark = currentTheme() === 'dark';
    toggleButtons.forEach(function (btn) {
      var icon = btn.querySelector('i');
      if (icon) {
        icon.className = isDark ? 'bi bi-sun' : 'bi bi-moon-stars';
      }
    });
  }

  function setTheme(theme) {
    root.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateToggleIcons();
  }

  function setTheme(theme) {
  root.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  updateToggleIcons();
}

var savedTheme = localStorage.getItem('theme') || 'light';
setTheme(savedTheme);
  toggleButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      setTheme(currentTheme() === 'dark' ? 'light' : 'dark');
    });
  });

  updateToggleIcons();

  /* ---------------------------------------------------------------------
   * Mobile navbar: close the collapsed menu automatically after a link
   * inside it is tapped, so users aren't left with the menu open.
   * ------------------------------------------------------------------- */
  var mobileNav = document.getElementById('mobileNav');
  if (mobileNav && window.bootstrap) {
    mobileNav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        var instance = window.bootstrap.Collapse.getOrCreateInstance(mobileNav);
        instance.hide();
      });
    });
  }

});

document.addEventListener("DOMContentLoaded", function () {
  const toggleBtn = document.getElementById("chatbot-toggle");
  const closeBtn = document.getElementById("chatbot-close");
  const chatWindow = document.getElementById("chatbot-window");
  const chatMessages = document.getElementById("chatbot-messages");
  const chatInput = document.getElementById("chatbot-input");
  const sendBtn = document.getElementById("chatbot-send");
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  // ფანჯრის გაღება/დახურვა
  toggleBtn.addEventListener("click", () => {
    chatWindow.classList.toggle("d-none");
    if (!chatWindow.classList.contains("d-none")) {
      chatInput.focus();
    }
  });

  closeBtn.addEventListener("click", () => {
    chatWindow.classList.add("d-none");
  });

  // შეტყობინების გაგზავნის ფუნქცია
  function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // 1. იუზერის ტექსტის გამოჩენა
    appendMessage(text, "user-message");
    chatInput.value = "";

    // 2. Loading ანიმაციის დამატება
    const typingId = showTypingIndicator();

    // 3. API-სთან დაკავშირება (Flask ბექენდი)
    fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken // CSRF დაცვისთვის აუცილებელია!
      },
      body: JSON.stringify({ message: text })
    })
    .then(response => response.json())
    .then(data => {
      removeTypingIndicator(typingId);
      if(data.reply) {
        appendMessage(data.reply, "bot-message");
      } else {
        appendMessage("ბოდიში, დაფიქსირდა შეცდომა.", "bot-message");
      }
    })
    .catch(error => {
      console.error("Chatbot Error:", error);
      removeTypingIndicator(typingId);
      appendMessage("კავშირის პრობლემაა. სცადეთ მოგვიანებით.", "bot-message");
    });
  }

  // ღილაკზე დაჭერით გაგზავნა
  sendBtn.addEventListener("click", sendMessage);

  // Enter კლავიშზე გაგზავნა
  chatInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      sendMessage();
    }
  });

  // DOM-ში მესიჯის დამატება
  function appendMessage(text, className) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `chat-message ${className}`;
    msgDiv.textContent = text;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight; // ავტომატური სქროლი
  }

  // Typing ანიმაციის ფუნქციები
  function showTypingIndicator() {
    const id = "typing-" + Date.now();
    const typingDiv = document.createElement("div");
    typingDiv.className = "typing-indicator";
    typingDiv.id = id;
    typingDiv.innerHTML = "<span></span><span></span><span></span>";
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
  }

  function removeTypingIndicator(id) {
    const typingDiv = document.getElementById(id);
    if (typingDiv) {
      typingDiv.remove();
    }
  }
});