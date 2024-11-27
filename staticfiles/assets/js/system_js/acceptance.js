const acceptContainer = document.getElementById('accept-form-wraper')
const responseContainer = document.getElementById('response-form-wraper')
const addParcelContainer = document.getElementById('add-form-wraper')
const acceptBtn = document.getElementById('save-accept-btn')
const addResponseBtn = document.getElementById('add-response-btn')
const addParcelBtn = document.getElementById('save-parcel-btn')
const awbBtn = document.getElementById('add-awb-btn');

const idWIdth = document.getElementById('id_width')
const idHeight = document.getElementById('id_height')
const idLength = document.getElementById('id_length')
const idVolume = document.getElementById('id_volume')



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
//    }
//    const csrftoken = getCookie('csrftoken');

function hideacceptform(e){
    e.preventDefault()

    $.ajax({
        type: 'POST',
        url: "/sifex/accept/",
        data: {
            'csrfmiddlewaretoken': csrftoken,
            'awb': document.getElementById('id_awb').value,
            'order_number': document.getElementById('id_order_number').value,
            'sender_name': document.getElementById('id_sender_name').value,
            'sender_name': document.getElementById('id_sender_name').value,
            'sender_tel': document.getElementById('id_sender_tel').value,
            'sender_address': document.getElementById('id_sender_address').value,
            'sender_city': document.getElementById('id_sender_city').value,
            'sender_country': document.getElementById('id_sender_country').value,
            'receiver_name': document.getElementById('id_receiver_name').value,
            'receiver_address': document.getElementById('id_receiver_address').value,
            'receiver_tel': document.getElementById('id_receiver_tel').value,
            'receiver_city': document.getElementById('id_receiver_city').value,
            'receiver_country': document.getElementById('id_receiver_country').value,
            'awb_type': document.getElementById('id_awb_type').value,
            'desc': document.getElementById('id_desc').value,
            'freight': document.getElementById('id_freight').value,
            'insurance': document.getElementById('id_insurance').value,
            'awb_pcs': document.getElementById('id_awb_pcs').value,
            'awb_kg': document.getElementById('id_awb_kg').value,
            'chargable_weight': document.getElementById('id_chargable_weight').value,
            'terms': document.getElementById('id_terms').value,
            'volume': document.getElementById('id_volume').value,
            'width': document.getElementById('id_width').value,
            'height': document.getElementById('id_height').value,
            'length': document.getElementById('id_length').value,
            'currency': document.getElementById('id_currency').value,
            'date_received': document.getElementById('id_date_received').value,
            'expected_arrival_date': document.getElementById('id_expected_arrival_date').value,
            'custom_value': document.getElementById('id_custom_value').value,
            'payment_mode': document.getElementById('id_payment_mode').value,

        },
        success: (res)=>{
            acceptContainer.classList.add('hide-accept-form')
            responseContainer.classList.remove('hide-response-form')
            responseContainer.innerHTML += `
            <div class="card-body">
            <form method="post" id="response-form" class="accept-form" enctype="multipart/form-data">
            <div class="row">
                <div class="col-lg-6 col-md-5 col-sm-6 col-12">
                    <div class="form-group">
                        <label for="awb" class="">AWB</label>
                        <input type="text" disabled class="form-control" id="id_awb" value="${res.awb}">
                        <input type="text" disabled class="form-control" hidden id="parcel_id" value="${res.id}">
                    </div>
                </div>
                <div class="col-lg-6 col-md-5 col-sm-6 col-12">
                    <div class="form-group">
                        <label for="order_number" class="">order number</label>
                        <input type="text" disabled class="form-control" id="id_order_number" value="${res.order_number}">
                    </div>
                </div>
            </div>
            <div class="otherfields mb-3">
                <div class="row">
                    <div class="col-md-4 col-lg-4 col-sm-12 col-12">
                        <label for="desc">Desc</label>
                        <input type="text" disabled class="form-control" id="id_desc" value="${res.desc}">
                    </div>
                    <div class="col-md-4 col-lg-4 col-sm-4 col-4">
                        <label for="freight">freight</label>
                        <input type="text" disabled class="form-control" id="id_freight" value="${res.freight}">
                    </div>
                    <div class="col-md-4 col-lg-4 col-sm-12 col-12">
                        <label for="insurance">insurance</label>
                        <input type="text" disabled class="form-control" id="id_insurance" value="${res.insurance}">
                    </div>
                
                    <div class="col-md-2 col-lg-2 col-sm-6 col-6">
                        <label for="awb_pcs">AWB pcs</label>
                        <input type="text" disabled class="form-control" id="id_awb_pcs" value="${res.awb_pcs}">
                    </div>
                    <div class="col-md-2 col-lg-2 col-sm-6 col-6">
                        <label for="awb_kg">AWB kg</label>
                        <input type="text" disabled class="form-control" id="id_awb_kg" value="${res.awb_kg}">
                    </div>
                    <div class="col-md-2 col-lg-2 col-sm-6 col-6">
                        <label for="chargable_weight">C.W</label>
                        <input type="text" disabled class="form-control" id="id_chargable_weight" value="${res.chargable_weight}">
                    </div>
                    <div class="col-md-2 col-lg-2 col-sm-12 col-12">
                        <label for="terms">terms</label>
                        <input type="text" disabled class="form-control" id="id_terms" value="${res.terms}">
                    </div>
                    
                    <div class="col-md-3 col-lg-3 col-sm-12 col-12">
                        <label for="volume">Volume</label>
                        <input type="text" disabled class="form-control" id="id_volume" value="${res.volume}">
                    </div>
                    <div class="col-md-2 col-lg-2 col-sm-12 col-12">
                        <label for="height">height</label>
                        <input type="text" disabled class="form-control" id="id_height" value="${res.height}">
                    </div>
                    <div class="col-md-2 col-lg-2 col-sm-12 col-12">
                        <label for="width">width</label>
                        <input type="text" disabled class="form-control" id="id_width" value="${res.width}">
                    </div>
                    <div class="col-md-2 col-lg-2 col-sm-2 col-2">
                        <label for="length">length</label>
                        <input type="text" disabled class="form-control" id="id_length" value="${res.length}">
                    </div>
                    <div class="col-md-2 col-lg-2 col-sm-6 col-6">
                        <label for="dlv_kg">currency</label>
                        <input type="text" disabled class="form-control" id="id_currency" value="${res.currency}">
                    </div>
                    <div class="col-md-2 col-lg-2 col-sm-6 col-6">
                        <label for="dlv_kg">date received</label>
                        <input type="text" disabled class="form-control" id="id_date_received" value="${res.date_received}">
                    </div>
                    <div class="col-md-2 col-lg-2 col-sm-6 col-6">
                        <label for="dlv_kg">expected arrival date</label>
                        <input type="text" disabled class="form-control" id="id_expected_arrival_date" value="${res.expected_arrival_date}">
                    </div>
                    <div class="col-md-2 col-lg-2 col-sm-6 col-6">
                    <label for="awb_type">awb type</label>
                    <input type="text" disabled class="form-control" id="id_awb_type" value="${res.awb_type}">
                </div>
                    <!--  -->
                    <div class="col-md-6 col-lg-6 col-sm-6 col-6">
                        <label for="custom_value">custom value</label>
                        <input type="text" disabled class="form-control" id="id_custom_value" value="${res.custom_value}">
                    </div>
                    <div class="col-md-6 col-lg-6 col-sm-6 col-6">
                        <label for="payment_mode">payment mode</label>
                        <input type="text" disabled class="form-control" id="id_payment_mode" value="${res.payment_mode}">
                    </div>
                </div>
            </div>
            <div class="row m-9">
                <div class="col-lg-8 col-md-8 col-sm-6 col-6">
                    <div class="row mt-9">
                        <div class="col-md-3 col-lg-3 col-sm-4">
                            <button type="button" id="save-response-btn" class="btn btn-primary disabled"> save</button>
                        </div>
                        <div class="col-md-3 col-lg-3 col-sm-4">
                            <button disabled type="button" id="edit-response-btn" class="btn btn-primary disabled"> edit</button>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4 col-md-4 col-sm-6 col-6">
                    <div class="row">
                        <div class="col-md-4 col-lg-4 col-sm-4">
                            <a href="/sifex/accept_console/" class="btn btn-danger">cancel</a>
                        </div>
                    </div>
                </div>
            </div>
        </form>
    </div>
            
    `
        const addBtn = document.getElementById('add-parcel-btn')
        function showAddParccelForm(){
            addParcelContainer.classList.remove('hide-add-form')
        }

        addBtn.addEventListener('click', showAddParccelForm);
        },
        error: (err)=>{
            console.log(err)
        }
    });
}



function sendAddParcel(e){
    e.preventDefault()
    $.ajax({
        type: 'POST',
        url: '/sifex/save_parcel/',
        data: {
            'csrfmiddlewaretoken': csrftoken,
            'id': document.getElementById('parcel_id').value,
            'desc': document.getElementById('res_id_desc').value,
            'freight': document.getElementById('res_id_freight').value,
            'insurance': document.getElementById('res_id_insurance').value,
            'awb_pcs': document.getElementById('res_id_awb_pcs').value,
            'awb_kg': document.getElementById('res_id_awb_kg').value,
            'chargable_weight': document.getElementById('res_id_chargable_weight').value,
            'terms': document.getElementById('res_id_terms').value,
            'volume': document.getElementById('res_id_volume').value,
            'width': document.getElementById('res_id_width').value,
            'height': document.getElementById('res_id_height').value,
            'length': document.getElementById('res_id_length').value,
            'currency': document.getElementById('res_id_currency').value,
            'date_received': document.getElementById('res_id_date_received').value,
            'expected_arrival_date': document.getElementById('res_id_expected_arrival_date').value,
            'custom_value': document.getElementById('res_id_custom_value').value,
            'payment_mode': document.getElementById('res_id_payment_mode').value,

        },
        success: (response)=>{
            console.log(response)
            addParcelContainer.classList.add('hide-add-form')
        },
        error: (err)=>{
            console.log(err)
        },
    })
}

acceptBtn.addEventListener('click', hideacceptform);
addParcelBtn.addEventListener('click', sendAddParcel);



function getKeys(){

       
var today = new Date();
var mydate = today.getDate();

var myDay = today.getUTCDay();
var tt = today.getTime();
var myhrs = today.getHours();
var myminutes = today.getMinutes();
var myseconds = today.getSeconds();

var mymonth = today.getMonth()+1; 
var myyear = today.getFullYear().toString().substr(-2);
if(mydate<10) 
{
    mydate='0'+mydate;
} 

if(mymonth<10) 
{
    mymonth='0'+mymonth;
} 

today = 'SX'+mydate+''+mymonth+''+myyear+''+myhrs+''+myminutes+''+myseconds+''+myDay;

document.getElementById("id_awb").value = today;
}

document.getElementById('awb-btn').addEventListener("click", getKeys);


function getParcelKeys(){

       
    var today = new Date();
    var mydate = today.getDate();
    
    var myDay = today.getUTCDay();
    var tt = today.getTime();
    var myhrs = today.getHours();
    var myminutes = today.getMinutes();
    var myseconds = today.getSeconds();
    
    var mymonth = today.getMonth()+1; 
    var myyear = today.getFullYear().toString().substr(-2);
    if(mydate<10) 
    {
        mydate='0'+mydate;
    } 
    
    if(mymonth<10) 
    {
        mymonth='0'+mymonth;
    } 
    
    today = 'SX'+mydate+''+mymonth+''+myyear+''+myhrs+''+myminutes+''+myseconds+''+myDay;
    
    document.getElementById("res_id_awb").value = today;
}

document.getElementById('request-key').addEventListener("click", getParcelKeys);





