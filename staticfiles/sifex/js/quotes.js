
const quoteFORM = document.getElementById('quote-form');
const sendername = document.getElementById('sendername');
const senderemail = document.getElementById('senderemail');
const senderphone = document.getElementById('senderphone');
const senderservice = document.getElementById('senderservice');
const quoteBTN = document.getElementById('send-request-btn');

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
   }
   const csrftoken = getCookie('csrftoken');




// const requestQuote = (e) => {
//     e.preventDefault()
//     $.ajax({
//         type: 'POST',
//         url: '/request_quote/',
//         data: {
//             'csrfmiddlewaretoken': csrftoken,
//             'name': sendername,
//             'email': senderemail,
//             'phone': senderphone,
//             'service': senderservice,
//         },
//         success: function(response){
//             console.log(response)
//         },
//         error: function(error){
//             console.log(error)
//         },
//     });
// }

// quoteBTN.addEventListener('click', requestQuote)




