let currentAttemptId = null;
let examData = null;
let currentQuestionIndex = 0;
let responses = {};

async function initExamRuntime(attemptId) {
    currentAttemptId = attemptId;
    
    // Integrity Monitoring
    document.addEventListener("visibilitychange", () => {
        if (document.hidden) {
            logIntegrity('tab_switch');
        }
    });
    
    // Fetch exam content
    const response = await fetch(`/api/examinations/${attemptId}/content`);
    examData = await response.json();
    
    document.getElementById('exam-name').innerText = examData.exam_name;
    
    renderPalette();
    renderQuestion(0);
    startTimer(examData.duration_minutes * 60);

    document.getElementById('next-btn').addEventListener('click', () => navigate(1));
    document.getElementById('prev-btn').addEventListener('click', () => navigate(-1));
}

async function logIntegrity(eventType) {
    await fetch(`/api/examinations/${currentAttemptId}/integrity`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({event_type: eventType})
    });
}

function renderPalette() {
    const paletteGrid = document.getElementById('palette-grid');
    paletteGrid.innerHTML = '';
    
    let qCount = 0;
    examData.components.forEach(comp => {
        comp.questions.forEach((_, qIndex) => {
            const btn = document.createElement('button');
            btn.className = "p-2 border rounded hover:bg-blue-100";
            btn.innerText = qCount + 1;
            btn.onclick = () => renderQuestion(qCount);
            paletteGrid.appendChild(btn);
            qCount++;
        });
    });
}

function renderQuestion(index) {
    currentQuestionIndex = index;
    const container = document.getElementById('question-container');
    
    let qCount = 0;
    let targetQuestion = null;
    let targetComponentId = null;
    
    examData.components.forEach(comp => {
        comp.questions.forEach(q => {
            if (qCount === index) {
                targetQuestion = q;
                targetComponentId = comp.id;
            }
            qCount++;
        });
    });
    
    container.innerHTML = `
        <h3 class="text-xl font-semibold mb-4">${targetQuestion.content.text || 'Question'}</h3>
        <div class="space-y-2">
            ${targetQuestion.options.map(opt => `
                <label class="block p-3 border rounded hover:bg-gray-50">
                    <input type="radio" name="q-${targetQuestion.id}" value="${opt.id}" 
                           ${responses[targetQuestion.id] === opt.id ? 'checked' : ''} 
                           onchange="saveResponse('${targetQuestion.id}', '${opt.id}', '${targetComponentId}')">
                    ${opt.content}
                </label>
            `).join('')}
        </div>
    `;
}

function navigate(direction) {
    const allQuestions = examData.components.flatMap(c => c.questions);
    const newIndex = currentQuestionIndex + direction;
    if (newIndex >= 0 && newIndex < allQuestions.length) {
        renderQuestion(newIndex);
    }
}

async function saveResponse(questionId, optionId, componentId) {
    responses[questionId] = optionId;
    
    // Auto-save via AJAX
    await fetch('/api/responses/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            attempt_id: currentAttemptId,
            component_id: componentId,
            question_id: questionId,
            response_mode: 'mcq',
            content: {option_id: optionId}
        })
    });
}

function startTimer(seconds) {
    const timerDisplay = document.getElementById('timer');
    let timeLeft = seconds;
    
    const interval = setInterval(() => {
        timeLeft--;
        const mins = Math.floor(timeLeft / 60);
        const secs = timeLeft % 60;
        timerDisplay.innerText = `${mins}:${secs.toString().padStart(2, '0')}`;
        
        if (timeLeft <= 0) clearInterval(interval);
    }, 1000);
}
