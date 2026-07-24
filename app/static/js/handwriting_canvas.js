function initHandwritingCanvas(canvasId, attemptId, componentId, questionId) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    let drawing = false;
    let strokes = [];
    let currentStroke = [];

    canvas.addEventListener('mousedown', (e) => {
        drawing = true;
        currentStroke = [{x: e.offsetX, y: e.offsetY}];
        ctx.beginPath();
        ctx.moveTo(e.offsetX, e.offsetY);
    });

    canvas.addEventListener('mousemove', (e) => {
        if (!drawing) return;
        ctx.lineTo(e.offsetX, e.offsetY);
        ctx.stroke();
        currentStroke.push({x: e.offsetX, y: e.offsetY});
    });

    canvas.addEventListener('mouseup', () => {
        drawing = false;
        strokes.push(currentStroke);
    });
    
    return {
        clear: () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            strokes = [];
        },
        save: async () => {
            const dataUrl = canvas.toDataURL();
            await fetch('/api/responses/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    attempt_id: attemptId,
                    component_id: componentId,
                    question_id: questionId,
                    response_mode: 'handwriting',
                    content: { strokes, dataUrl }
                })
            });
        }
    };
}
