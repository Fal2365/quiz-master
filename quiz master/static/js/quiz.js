function startTimer(duration) {
    let timer = duration;       
    let display = document.getElementById("timer"); 

    let countdown = setInterval(function () {
        let minutes = Math.floor(timer / 60);
        let seconds = timer % 60;

        display.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;

        if (timer <= 0) {
            clearInterval(countdown);
            document.getElementById("submit-button").click(); 
        } else {
            timer--;
        }
    }, 1000);
}

window.onload = function () {
    let time = document.getElementById("timer").textContent;
    let [minutes, seconds] = time.split(":").map(Number);
    let timeInSeconds = minutes * 60 + seconds;
    startTimer(timeInSeconds);
};






