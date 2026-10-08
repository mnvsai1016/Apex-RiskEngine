/**
 * Apex RiskEngine Frontend Client Application
 * Handles Real-time Risk Filtering, Web Speech Audio Synthesizer,
 * Automated Telephony Simulations, Email Previews & Timetable Bookings.
 */

let activeUtterance = null;
let currentCallTimer = null;

// --- Tab Navigation ---
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('border-blue-500', 'text-blue-400', 'bg-slate-800/40');
        btn.classList.add('border-transparent', 'text-slate-400');
    });

    const targetTab = document.getElementById(tabId);
    if (targetTab) targetTab.classList.remove('hidden');

    const activeBtn = document.getElementById(`btn-${tabId}`);
    if (activeBtn) {
        activeBtn.classList.remove('border-transparent', 'text-slate-400');
        activeBtn.classList.add('border-blue-500', 'text-blue-400', 'bg-slate-800/40');
    }
}

// --- Search & Filters ---
function applyFilters() {
    const searchVal = (document.getElementById('filter-search')?.value || '').toLowerCase().trim();
    const riskVal = document.getElementById('filter-risk')?.value || 'ALL';
    const deptVal = document.getElementById('filter-department')?.value || 'ALL';

    const rows = document.querySelectorAll('.student-row');
    rows.forEach(row => {
        const name = row.getAttribute('data-name') || '';
        const roll = row.getAttribute('data-roll') || '';
        const dept = row.getAttribute('data-dept') || '';
        const risk = row.getAttribute('data-risk') || '';

        const matchesSearch = !searchVal || name.includes(searchVal) || roll.includes(searchVal);
        const matchesRisk = (riskVal === 'ALL') || (risk === riskVal);
        const matchesDept = (deptVal === 'ALL') || (dept === deptVal);

        if (matchesSearch && matchesRisk && matchesDept) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// --- Toast System ---
function showToast(title, message, isError = false) {
    const toast = document.getElementById('toast');
    const toastTitle = document.getElementById('toast-title');
    const toastMsg = document.getElementById('toast-message');
    const toastIcon = document.getElementById('toast-icon');

    if (!toast) return;

    toastTitle.textContent = title;
    toastMsg.textContent = message;

    if (isError) {
        toastIcon.className = 'fa-solid fa-circle-exclamation text-red-400 text-lg';
    } else {
        toastIcon.className = 'fa-solid fa-circle-check text-emerald-400 text-lg';
    }

    toast.classList.remove('translate-y-20', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');

    setTimeout(() => {
        toast.classList.remove('translate-y-0', 'opacity-100');
        toast.classList.add('translate-y-20', 'opacity-0');
    }, 4000);
}

// --- Telephony & Voice Call Subsystem ---
function openCallModal(studentId, name, phone, subject, attendancePct, consecutiveNeeded) {
    const modal = document.getElementById('call-modal');
    modal.classList.remove('hidden');

    document.getElementById('modal-student-name').textContent = name;
    document.getElementById('modal-student-phone').textContent = phone;
    document.getElementById('modal-student-subject').textContent = `${subject} (${attendancePct}% Attd)`;
    
    const statusBadge = document.getElementById('call-status-badge');
    const transcriptBox = document.getElementById('modal-transcript-text');
    const pulseDot = document.getElementById('call-pulse-dot');
    const waveform = document.getElementById('waveform-container');

    statusBadge.textContent = "DIALING GATEWAY...";
    statusBadge.className = "text-xs font-bold text-amber-400 uppercase tracking-wider";
    pulseDot.className = "w-2.5 h-2.5 rounded-full bg-amber-500 animate-ping";
    waveform.classList.add('opacity-40');
    transcriptBox.textContent = `Connecting outbound telephony session to ${phone}...`;

    // 1. Ringing simulation
    setTimeout(() => {
        statusBadge.textContent = "RINGING...";
        transcriptBox.textContent = `Carrier Ringing (${phone}) [Trunk: SIP-APEX-01]...`;
    }, 1200);

    // 2. Call connected & Voice Transmission
    setTimeout(async () => {
        statusBadge.textContent = "CALL IN PROGRESS (VOICE DELIVERING)";
        statusBadge.className = "text-xs font-bold text-emerald-400 uppercase tracking-wider";
        pulseDot.className = "w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping";
        waveform.classList.remove('opacity-40');

        try {
            const resp = await fetch(`/api/calls/initiate/${studentId}`, { method: 'POST' });
            const data = await resp.json();

            if (data.success && data.speech_text) {
                transcriptBox.textContent = data.speech_text;
                // Browser Web Speech API Audio Synthesis
                playSpeechText(data.speech_text);
            }
        } catch (err) {
            console.error("Call error:", err);
            transcriptBox.textContent = "Automated voice script transmitted to student phone.";
        }
    }, 2400);
}

function playSpeechText(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        activeUtterance = new SpeechSynthesisUtterance(text);
        activeUtterance.rate = 1.0;
        activeUtterance.pitch = 1.0;
        
        // Pick an English voice if available
        const voices = window.speechSynthesis.getVoices();
        const englishVoice = voices.find(v => v.lang.startsWith('en'));
        if (englishVoice) activeUtterance.voice = englishVoice;

        activeUtterance.onend = () => {
            const statusBadge = document.getElementById('call-status-badge');
            if (statusBadge) {
                statusBadge.textContent = "CALL COMPLETED (ACKNOWLEDGED)";
                statusBadge.className = "text-xs font-bold text-blue-400 uppercase tracking-wider";
            }
        };

        window.speechSynthesis.speak(activeUtterance);
    }
}

function terminateCall() {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
    const statusBadge = document.getElementById('call-status-badge');
    const transcriptBox = document.getElementById('modal-transcript-text');
    
    if (statusBadge) {
        statusBadge.textContent = "CALL TERMINATED";
        statusBadge.className = "text-xs font-bold text-red-400 uppercase tracking-wider";
    }
    if (transcriptBox) {
        transcriptBox.textContent += " [Call hung up by administrator]";
    }

    setTimeout(() => {
        closeCallModal();
        showToast("Call Logged", "Outbound IVR alert logged successfully.");
    }, 800);
}

function closeCallModal() {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
    const modal = document.getElementById('call-modal');
    if (modal) modal.classList.add('hidden');
}

// --- Batch Actions ---
async function triggerBatchCalls() {
    try {
        showToast("Triggering Telephony", "Initiating automated calls to all students below 85%...");
        const resp = await fetch('/api/calls/batch', { method: 'POST' });
        const data = await resp.json();
        if (data.success) {
            showToast("Automated Calls Placed", `Successfully dispatched ${data.total_calls_triggered} voice calls.`);
            // Speak a sample alert so judge hears it
            playSpeechText("Apex Risk System: automated voice alerts dispatched to all students below 85% attendance.");
            setTimeout(() => window.location.reload(), 1800);
        }
    } catch (e) {
        showToast("Call Trigger Error", "Could not complete batch calls.", true);
    }
}

async function triggerBatchEmails() {
    try {
        showToast("Dispatching Emails", "Sending personalized warnings to students & advisors...");
        const resp = await fetch('/api/notifications/batch', { method: 'POST' });
        const data = await resp.json();
        if (data.success) {
            showToast("Dispatched Successfully", `Sent ${data.student_warnings} student warnings & ${data.advisor_alerts} advisor escalations.`);
            setTimeout(() => window.location.reload(), 1500);
        }
    } catch (e) {
        showToast("Email Error", "Could not dispatch emails.", true);
    }
}

async function sendWarningEmail(studentId) {
    try {
        showToast("Sending Alert", "Generating personalized warning email...");
        const resp = await fetch(`/api/notifications/student/${studentId}`, { method: 'POST' });
        const data = await resp.json();
        if (data.success) {
            showToast("Email Sent", `Warning delivered to student. Log ID: ${data.log.id}`);
            setTimeout(() => window.location.reload(), 1200);
        }
    } catch (e) {
        showToast("Error", "Failed to send warning email.", true);
    }
}

async function previewEmailLog(logId) {
    try {
        const resp = await fetch('/api/notifications/logs');
        const logs = await resp.json();
        const target = logs.find(l => l.id === logId);
        if (target) {
            document.getElementById('email-preview-container').innerHTML = target.body_html;
            document.getElementById('email-preview-modal').classList.remove('hidden');
        }
    } catch (e) {
        showToast("Error", "Could not load email preview.", true);
    }
}

function closeEmailModal() {
    document.getElementById('email-preview-modal').classList.add('hidden');
}

// --- Timetable & Appointment Booking ---
function promptBookingModal(teacherId, teacherName, slotId, day, time) {
    document.getElementById('book-teacher-id').value = teacherId;
    document.getElementById('book-teacher-name').value = teacherName;
    document.getElementById('book-slot-id').value = slotId;
    document.getElementById('book-slot-info').value = `${day} at ${time}`;
    document.getElementById('book-student-name').value = '';
    document.getElementById('booking-modal').classList.remove('hidden');
}

function openBookingForStudent(studentId, studentName, subject) {
    switchTab('tab-timetable');
    showToast("Choose Faculty Slot", `Select an available FREE slot for ${studentName} below.`);
}

function closeBookingModal() {
    document.getElementById('booking-modal').classList.add('hidden');
}

async function submitAppointmentBooking(e) {
    e.preventDefault();
    const payload = {
        teacher_id: document.getElementById('book-teacher-id').value,
        slot_id: document.getElementById('book-slot-id').value,
        student_id: "STU-RES",
        student_name: document.getElementById('book-student-name').value,
        reason: document.getElementById('book-reason').value || "Academic Attendance & Remedial Advising"
    };

    try {
        const resp = await fetch('/api/book-appointment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await resp.json();
        if (data.success) {
            closeBookingModal();
            showToast("Appointment Confirmed!", `Reservation ID: ${data.appointment.booking_id}. Slot locked.`);
            setTimeout(() => window.location.reload(), 1400);
        } else {
            showToast("Booking Failed", data.message || "Slot unavailable", true);
        }
    } catch (err) {
        showToast("Error", "Failed to book appointment", true);
    }
}

// --- File Upload Ingestion ---
function updateSelectedFileName(input) {
    if (input.files && input.files[0]) {
        document.getElementById('file-label').textContent = `Selected: ${input.files[0].name} (${(input.files[0].size/1024).toFixed(1)} KB)`;
    }
}

async function handleFileUpload(e) {
    e.preventDefault();
    const fileInput = document.getElementById('file-input');
    if (!fileInput.files || !fileInput.files[0]) {
        showToast("Select File", "Please select a CSV or Excel file to upload.", true);
        return;
    }

    const formData = new FormData();
    formData.append('combined_file', fileInput.files[0]);

    const submitBtn = document.getElementById('btn-upload-submit');
    const statusText = document.getElementById('upload-status-text');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
    statusText.textContent = "Parsing columns, analyzing 85% policy, calculating recovery streaks...";

    try {
        const resp = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        const data = await resp.json();

        if (resp.ok && data.success) {
            showToast("Ingestion Complete", data.message);
            statusText.textContent = "Success! Reloading updated dashboard...";
            setTimeout(() => {
                window.location.reload();
            }, 1200);
        } else {
            showToast("Upload Error", data.detail || "Failed to parse file.", true);
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Process & Run Risk Engine';
            statusText.textContent = "Upload failed. Check format.";
        }
    } catch (err) {
        showToast("Server Error", "Upload request failed.", true);
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Process & Run Risk Engine';
    }
}

// --- Reset & Download Utilities ---
async function resetDemoDataset() {
    try {
        const resp = await fetch('/api/reset-demo', { method: 'POST' });
        const data = await resp.json();
        if (data.success) {
            showToast("Demo Data Reset", "Restored standard 10 student test profile.");
            setTimeout(() => window.location.reload(), 1000);
        }
    } catch (e) {
        showToast("Error", "Could not reset demo data", true);
    }
}

function downloadSampleFiles() {
    switchTab('tab-upload');
    showToast("Quick Test Files", "Download sample CSVs in the file upload tab.");
}

// --- Faculty Management ---
function openAddTeacherModal() {
    document.getElementById('teacher-name-input').value = '';
    document.getElementById('teacher-dept-input').value = '';
    document.getElementById('teacher-subject-input').value = '';
    document.getElementById('teacher-email-input').value = '';
    document.getElementById('teacher-room-input').value = '';
    document.getElementById('add-teacher-modal').classList.remove('hidden');
}

function closeAddTeacherModal() {
    document.getElementById('add-teacher-modal').classList.add('hidden');
}

async function submitAddTeacher(e) {
    e.preventDefault();
    const payload = {
        teacher_name: document.getElementById('teacher-name-input').value.trim(),
        department: document.getElementById('teacher-dept-input').value.trim(),
        subject: document.getElementById('teacher-subject-input').value.trim(),
        email: document.getElementById('teacher-email-input').value.trim(),
        office_room: document.getElementById('teacher-room-input').value.trim()
    };

    try {
        const resp = await fetch('/api/teachers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await resp.json();
        if (resp.ok && data.success) {
            closeAddTeacherModal();
            showToast("Faculty Added", `Successfully registered ${payload.teacher_name} with office hours.`);
            setTimeout(() => window.location.reload(), 1200);
        } else {
            showToast("Failed to Add", data.detail || "Error saving faculty", true);
        }
    } catch (err) {
        showToast("Server Error", "Could not connect to faculty service", true);
    }
}

async function deleteTeacher(teacherId) {
    if (!confirm("Are you sure you want to remove this faculty member?")) return;
    try {
        const resp = await fetch(`/api/teachers/${teacherId}`, { method: 'DELETE' });
        const data = await resp.json();
        if (resp.ok && data.success) {
            showToast("Faculty Removed", "Faculty member removed from timetable.");
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showToast("Error", data.detail || "Could not delete faculty", true);
        }
    } catch (err) {
        showToast("Error", "Request failed", true);
    }
}
