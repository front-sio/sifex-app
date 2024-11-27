

const postBOX = document.getElementById('post-box');


$.ajax({
    type: 'GET',
    url: '/get_posts/',
    success: function(response){
        console.log(response)
        data = response.data 
        data.forEach(post => {
        postBOX.innerHTML += `
            <div class="card mb-5">
                <div class="card-body">
                    <h4>${post.title}</h4>
                    <p>${post.body}</p>
                </div>
            </div>
        `
        });
    },
    error: function(err){
        console.log(err)
    }
});