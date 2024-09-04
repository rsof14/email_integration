console.log('test local');
let login = localStorage.getItem('login');
let password = localStorage.getItem('password');
if (!login || !password) {
    window.location.href = 'login';
        }
let domain = getDomain(login)
let socket = new WebSocket('ws://localhost:8000/ws/email/')
socket.onopen = function() {
                console.log('WebSocket connection opened');
                socket.send(JSON.stringify({'emailServer': domain, 'login': login, 'password': password}));
            };

socket.onmessage = function(event){
    let djangoData = JSON.parse(event.data);
    console.log(djangoData);
    let searching = djangoData.searching_latest;
    if (searching == 'True') {
        let now = djangoData.progress_bar.progress;
        let max = djangoData.progress_bar.messages_numb;
        const progressDiv = document.getElementById('progressbar');
        progressDiv.style.width = (now / max * 100).toString() + '%';
        progressDiv.innerHTML = 'Чтение сообщений';
        console.log((now / max * 100).toString() + '%');
        progressDiv.setAttribute('aria-valuenow', (now / max * 100).toString() + '%');
        console.log(progressDiv)
        }
    let loading = djangoData.loading_emails;
    if (loading == 'True') {
        let now = djangoData.progress_bar.progress;
        let max = djangoData.progress_bar.messages_numb;
        const progressDiv = document.getElementById('progressbar');
        progressDiv.style.width = (now / max * 100).toString() + '%';
        progressDiv.innerHTML = 'Получение сообщений';
        console.log((now / max * 100).toString() + '%');
        progressDiv.setAttribute('aria-valuenow', (now / max * 100).toString() + '%');

        msg = djangoData.email.message;
        if (msg.length > 150) {
            msg = djangoData.email.message.slice(0, 150) + "...";
        }

        const tableBody = document.querySelector('#emails_table tbody');
        const row = tableBody.insertRow();
        const cellFrom = row.insertCell(0);
        const cellTopic = row.insertCell(1);
        const cellDate = row.insertCell(2);
        const cellMessage = row.insertCell(3);

        cellFrom.textContent = djangoData.email.from;
        cellTopic.textContent = djangoData.email.topic;
        cellDate.textContent = djangoData.email.send_date;
        cellMessage.textContent = msg;

    }

}

function getDomain(email) {
          const [, domain] = email.split('@');

          if (domain.endsWith('yandex.ru')) {
            return 'imap.yandex.ru';
          } else if (domain.endsWith('gmail.com')) {
            return 'imap.gmail.com';
          } else if (domain.endsWith('mail.ru')) {
            return 'imap.mail.ru';
          } else {
            return 'Unknown domain';
          }
        }