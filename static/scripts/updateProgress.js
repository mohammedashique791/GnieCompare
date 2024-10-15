const socket = io.connect();

let totalTasks = 8;
let completedTasks = 0;


socket.on('number_of_tasks', (data)=>{
    totalTasks = data.number
})

const progressBar = document.getElementById('progress-bar');
const websiteName = document.querySelector('.model');
const extractionContainer = document.querySelector('.extractionDetails')
const text = document.getElementById('extractText');
const myList = document.getElementById('theList')


// document.addEventListener('DOMContentLoaded', () => {
//     const fadeInElements = document.querySelectorAll('.fade-in');
//     fadeInElements.forEach(element => {
//         element.classList.add('visible');
//     });
// });

function updateTextWithLimit(newText) {
    if (newText.length > 50) {
        newText.substring(0, 50)
}
}

document.getElementById('start-button').addEventListener('click', function() {
    extractionContainer.style.display = 'block';
    extractionContainer.style.display = 'flex';
    updateTextWithLimit(text.textContent);
});



function updateProgress() {
    completedTasks += 1;
    const progressPercentage = (completedTasks / totalTasks) * 100;

    progressBar.style.width = progressPercentage + '%';
    progressBar.innerText = Math.round(progressPercentage) + '%';

    if (completedTasks === totalTasks) {
        progressBar.style.width = '100%';
        progressBar.innerText = '100%';
    }
}

function updateWebsite(url){
    websiteName.textContent = url
}

socket.on('update_progress', (data) => {
    // console.log('Progress update received:', data);
    updateProgress()
});


socket.on('process_completed', (data)=>{
    extractionContainer.style.display = 'none';
})

socket.on('update_url', (data)=>[
    updateWebsite(data.url)
])


socket.on('add_to_list', (data)=>{
    if (theList.innerHTML.trim() === "No Extracted Data Available.") {
        theList.innerHTML = '<li>' + data.url + '</li>';
    } else {
        theList.innerHTML += '<br>' + '<li>' + data.url + '</li>';
    }
})

function excel_downloading(){
    fetch('/download')
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'comparison_my_new_one.xlsx';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        })
        .catch(err => console.error('Error downloading Excel file:', err));
}

function startScraping(event){
    event.preventDefault();
    document.getElementById('progress-bar').style.width = "0%";
    document.getElementById('progress-bar').innerText = "0%";
    console.log("in start scraping function");

    fetch('/main', {
        method: "POST",
        body: new FormData(document.querySelector('form'))
    })
    .then(()=>{
        excel_downloading();
    })

    return false;
}