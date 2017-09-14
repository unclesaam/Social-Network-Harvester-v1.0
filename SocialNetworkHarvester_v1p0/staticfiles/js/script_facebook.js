window.fbAsyncInit = function() {
	FB.init({
		appId	: facebookAppId,
		xfbml	: true,
		version	: facebookAppVersion,
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
    if(fbAccessToken != 'None' && fbAccessToken != null ){
        log('current access token: '+fbAccessToken);
        FB.api("/me?fields=id,name,picture.type(large)&access_token="+ fbAccessToken, function(response){
            if(response['error']!= null){
                $('#tokenErrorMarker').show()
                $('#notLoggedInMessage').show()
                $('#custom_login_button').show()
                $('#custom_logout_button').hide()
                $('#login_infos_container').hide()
            } else {
                $('#userImg').attr('src', response.picture.data.url)
                $('#user_name').html(response.name)
                $('#notLoggedInMessage').hide()
                $('#custom_login_button').hide()
                $('#custom_logout_button').show()
                $('#login_infos_container').show()
                $('#tokenErrorMarker').hide()
            }
        })
    } else {
        FB.getLoginStatus(function (response) {
            //log(response)
            if (response.status === 'connected') {
                $('#notLoggedInMessage').hide()
                $('#custom_login_button').hide()
                $('#tokenErrorMarker').hide()
                $('#custom_logout_button').show()
                FB.api('/me?fields=id,name,picture', function (response) {
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
}

function facebookLogIn(){
    FB.login(function (response) {
        fbAccessToken = response.authResponse.accessToken;
        updateStoredToken(function(response){
            FB.logout();
            showLoggedIn();
        });
    })
}

function facebookLogout(){
    fbAccessToken = null;
    updateStoredToken(function(response){
        //FB.logout();
        showLoggedIn();
    })
}


function updateStoredToken(callback){
    $.ajax({
        type: 'POST',
        url: '/facebook/forms/setFacebookToken',
        data: {
            fbToken: fbAccessToken,
            csrfmiddlewaretoken: csrf_token,
        },
        success: function(response){callback(response)},
    })
}