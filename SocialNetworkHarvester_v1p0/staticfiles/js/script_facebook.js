window.fbAsyncInit = function() {
	FB.init({
		appId	: appID,
		xfbml	: true,
		version	: appVersion,
        status  : true,
    });
    showLoggedIn();
};

(function(d, s, id){
	var js, fjs = d.getElementsByTagName(s)[0];
	if (d.getElementById(id)) {return;};
	js = d.createElement(s);
	js.id = id;
	js.async = true;
	js.src = "//connect.facebook.net/en_US/sdk.js";
	fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));


function showLoggedIn(){
    FB.getLoginStatus(function (response) {
        if (response.status === 'connected') {
            $('#notLoggedInMessage').hide()
            $('#custom_login_button').hide()
            $('#custom_logout_button').show()
            log(FB)
            FB.api('/me?fields=id,name,picture', function (response) {
                log(response)
                $('#userImg').attr('src', response.picture.data.url)
                $('#user_name').html(response.name)
            })
            $('#login_infos_container').show()
        } else {
            $('#notLoggedInMessage').show()
            $('#custom_login_button').show()
            $('#custom_logout_button').hide()
            $('#login_infos_container').hide()
        }
    })
}

function logIn(){
    FB.login(function (response) {
        console.log(response);
        console.log(response.authResponse);
        console.log('accessToken:')
        console.log(response.authResponse.accessToken);
        $.ajax({
            type: 'POST',
            url: '/facebook/setFacebookToken',
            data: {
                token: response.authResponse.accessToken,
            },
            success: function (response) {
                console.log(response);
                showLoggedIn()
            },
        })
    })
}
function logout(){
    FB.logout(function(response){
        showLoggedIn()
    })
}

