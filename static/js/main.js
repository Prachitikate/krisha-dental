// ── SCROLL ANIMATIONS ─────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.12 });
  document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

  const navbar = document.querySelector('.kd-navbar');
  window.addEventListener('scroll', () => {
    navbar?.classList.toggle('scrolled', window.scrollY > 60);
  });

  document.querySelectorAll('.kd-alert').forEach(el => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert?.close();
    }, 5000);
  });
});

// ── FORM VALIDATION ────────────────────────────────────────
function validateBookingForm() {
  const fields = ['name', 'mobile', 'email', 'appointment_date', 'appointment_time', 'reason'];
  let valid = true;
  fields.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    const val = el.value.trim();
    if (!val) { showError(el, 'This field is required.'); valid = false; }
    else clearError(el);
  });
  const email = document.getElementById('email');
  if (email && email.value.trim()) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!re.test(email.value.trim())) { showError(email, 'Enter a valid email address.'); valid = false; }
  }
  const mobile = document.getElementById('mobile');
  if (mobile && mobile.value.trim()) {
    const re = /^[6-9]\d{9}$/;
    if (!re.test(mobile.value.trim())) { showError(mobile, 'Enter a valid 10-digit mobile number.'); valid = false; }
  }
  const dateEl = document.getElementById('appointment_date');
  if (dateEl && dateEl.value) {
    const today = new Date(); today.setHours(0,0,0,0);
    const sel = new Date(dateEl.value);
    if (sel < today) { showError(dateEl, 'Please select a future date.'); valid = false; }
  }
  return valid;
}

function validateLoginForm() {
  const email = document.getElementById('email');
  const password = document.getElementById('password');
  let valid = true;
  if (!email?.value.trim()) { showError(email, 'Email is required.'); valid = false; } else clearError(email);
  if (!password?.value.trim()) { showError(password, 'Password is required.'); valid = false; } else clearError(password);
  return valid;
}

function validateRegisterForm() {
  const fields = ['name', 'mobile', 'email', 'password'];
  let valid = true;
  fields.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    if (!el.value.trim()) { showError(el, 'This field is required.'); valid = false; }
    else clearError(el);
  });
  const mobile = document.getElementById('mobile');
  if (mobile && mobile.value.trim() && !/^[6-9]\d{9}$/.test(mobile.value.trim())) {
    showError(mobile, 'Enter a valid 10-digit mobile number.'); valid = false;
  }
  const pw = document.getElementById('password');
  if (pw && pw.value.trim() && pw.value.trim().length < 6) {
    showError(pw, 'Password must be at least 6 characters.'); valid = false;
  }
  return valid;
}

function showError(el, msg) {
  el.classList.add('is-invalid');
  let feedback = el.nextElementSibling;
  if (!feedback || !feedback.classList.contains('invalid-feedback')) {
    feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    el.parentNode.insertBefore(feedback, el.nextSibling);
  }
  feedback.textContent = msg;
}

function clearError(el) {
  el.classList.remove('is-invalid');
  const feedback = el.nextElementSibling;
  if (feedback && feedback.classList.contains('invalid-feedback')) feedback.textContent = '';
}

document.addEventListener('DOMContentLoaded', () => {
  const dateEl = document.getElementById('appointment_date');
  if (dateEl) {
    const today = new Date().toISOString().split('T')[0];
    dateEl.setAttribute('min', today);
  }
});

function openRescheduleModal(apptId) {
  document.getElementById('reschedule_appt_id').value = apptId;
  const modal = new bootstrap.Modal(document.getElementById('rescheduleModal'));
  modal.show();
}

function openDetailsModal(data) {
  const el = document.getElementById('detailsContent');
  if (!el) return;
  el.innerHTML = `
    <table class="table table-sm">
      <tr><th width="40%">Patient Name</th><td>${data.name}</td></tr>
      <tr><th>Mobile</th><td>${data.mobile}</td></tr>
      <tr><th>Email</th><td>${data.email}</td></tr>
      <tr><th>Date</th><td>${data.date}</td></tr>
      <tr><th>Time</th><td>${data.time}</td></tr>
      <tr><th>Reason</th><td>${data.reason}</td></tr>
      <tr><th>Branch</th><td>${data.branch}</td></tr>
      <tr><th>Status</th><td><span class="badge-status badge-${data.status}">${data.status}</span></td></tr>
      <tr><th>Booked At</th><td>${data.created_at}</td></tr>
    </table>`;
  new bootstrap.Modal(document.getElementById('detailsModal')).show();
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.toggle-pw').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = document.querySelector(btn.dataset.target);
      if (!input) return;
      const isText = input.type === 'text';
      input.type = isText ? 'password' : 'text';
      btn.querySelector('i').className = isText ? 'bi bi-eye' : 'bi bi-eye-slash';
    });
  });
});

// ── RULE-BASED CHATBOT ─────────────────────────────────────
const chatRules = [
  {
    keys: ['timing', 'time', 'open', 'hours', 'veles', 'वेळ', 'वेळा'],
    reply: '🕐 <b>Clinic Timings:</b><br>Mon–Sat: 10 AM to 10 PM<br>Sunday: 4 PM to 10 PM'
  },
  {
    keys: ['location', 'address', 'where', 'patta', 'पत्ता', 'kuth'],
    reply: '📍 <b>Our Locations:</b><br>1. Shop No 4, Radha Complex, Vimal Dairy Lane, Bhayandar East – 401105<br>2. Shop No 18, Govindpuri CHS, LTT Nilegaon, Nallasopara West – 401203'
  },
  {
    keys: ['service', 'treatment', 'dental', 'implant', 'root canal', 'braces', 'whitening', 'crown', 'bridge'],
    reply: '🦷 <b>Our Services:</b><br>• Dental Implants<br>• Root Canal Treatment<br>• Cosmetic Dentistry<br>• Crown, Bridge & Denture<br>• Pediatric Dentistry<br>• Braces & Orthodontics'
  },
  {
    keys: ['fee', 'fees', 'cost', 'price', 'charge', 'kitna', 'कितना', 'किती'],
    reply: '💰 <b>Fees:</b> Consultation is FREE! Treatment costs vary by procedure. Call us for exact pricing: <b>+91 9967628265</b>'
  },
  {
    keys: ['appointment', 'book', 'appoint', 'fix', 'schedule'],
    reply: '📅 <b>Book Appointment:</b> <a href="/book-appointment" style="color:#1e40af;">Click here to book online</a> or call <b>+91 9967628265</b>'
  },
  {
    keys: ['contact', 'phone', 'number', 'call', 'mobile', 'whatsapp'],
    reply: '📞 <b>Contact Us:</b><br>Number 1: <a href="tel:+918808828265">+91 8808828265</a><br>Number 2: <a href="tel:+919967628265">+91 9967628265</a><br><a href="https://wa.me/919967628265" target="_blank">💬 WhatsApp Us</a>'
  },
  {
    keys: ['doctor', 'dr', 'डॉक्टर', 'dentist', 'specialist'],
    reply: '👨‍⚕️ Our experienced dental team provides gentle, professional care for all ages. Visit us to meet our doctors!'
  },
  {
    keys: ['hello', 'hi', 'hey', 'hii', 'नमस्ते', 'namaste'],
    reply: '👋 Hello! Welcome to Krisha Dental Clinic. How can I help you today?'
  },
  {
    keys: ['thank', 'thanks', 'dhanyawad', 'धन्यवाद'],
    reply: '😊 You\'re welcome! Is there anything else I can help you with?'
  }
];

function getBotReply(msg) {
  const lower = msg.toLowerCase();
  for (const rule of chatRules) {
    if (rule.keys.some(k => lower.includes(k))) return rule.reply;
  }
  return '🤔 I\'m not sure about that. Please call us at <b>+91 9967628265</b> or visit our clinic for more info!';
}

function sendChatMessage(text) {
  const input = document.getElementById('chatInput');
  const messages = document.getElementById('chatMessages');
  if (!messages) return;
  const msg = text || input?.value.trim();
  if (!msg) return;
  if (input) input.value = '';

  // User message
  messages.innerHTML += `<div style="text-align:right;margin-bottom:10px;"><span style="background:#1e40af;color:white;padding:8px 14px;border-radius:18px 18px 4px 18px;display:inline-block;font-size:0.85rem;max-width:80%;">${msg}</span></div>`;

  // Bot reply
  const reply = getBotReply(msg);
  setTimeout(() => {
    messages.innerHTML += `<div style="text-align:left;margin-bottom:10px;"><span style="background:#f0f4ff;color:#1e293b;padding:8px 14px;border-radius:18px 18px 18px 4px;display:inline-block;font-size:0.85rem;max-width:85%;">${reply}</span></div>`;
    messages.scrollTop = messages.scrollHeight;
  }, 400);
  messages.scrollTop = messages.scrollHeight;
}

function toggleChat() {
  const box = document.getElementById('chatBox');
  if (!box) return;
  box.style.display = box.style.display === 'none' ? 'flex' : 'none';
}

document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('chatInput');
  input?.addEventListener('keydown', e => { if (e.key === 'Enter') sendChatMessage(); });
});
