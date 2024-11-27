// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         const cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             // Does this cookie string begin with the name we want?
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }
// const csrftoken = getCookie('csrftoken');



// const saveBtn = document.getElementById('form-save')
//     function sendData(e){
//         e.preventDefault()
//         console.log('btn clicked')
//         $.ajax({
//             type: 'POST',
//             url: '',
//             data: {
//                 'awb': $('#id_awb').val(),
//                 'order_number': $('#id_order_number').val(),
//                 'sender_name': $('#id_sender_name').val(),
//                 'csrfmiddlewaretoken': csrftoken,
//             },
//             success: (res)=>{
//                 console.log(res)
//             },
//             error: (error)=>{
//                 console.log(error)
//             },
//         })
//     }
//     saveBtn.addEventListener('click', function(e){
//         console.log('btn clicked')
//     })