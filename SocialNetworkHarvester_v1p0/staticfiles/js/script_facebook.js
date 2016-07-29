window.fbAsyncInit = function() {
	FB.init({
		appId	: '1747029368884864',
		xfbml	: true,
		version	: 'v2.7'
	});

	console.log('Api loaded');

	FB.login(function(response){
		console.log(response);
		console.log(response.authResponse);
		console.log(response.authResponse.accessToken);
		$.ajax({
            type:'POST',
            url:'/facebook/setFacebookToken',
            data:{
                token: response.authResponse.accessToken,
            },
            success: function (response) {
                console.log(response);
            },
        })
		console.log(response.authResponse.userID);
		var access_token = response.authResponse.accessToken;
		var userId = response.authResponse.userID;

		FB.api(
    		//"/" + userId + "?access_token=" + access_token,
    		"/me/permissions",
    		function (response) {
      			if (response && !response.error) {
        			console.log(response);
      			}
      			else{
      				console.log(response);
      			}
    		}
		);

		FB.api(
    		//"/" + userId + "?access_token=" + access_token,
    		"/me/posts",
    		function (response) {
      			if (response && !response.error) {
        			console.log(response);
      			}
      			else{
      				console.log(response);
      			}
    		}
		);

		FB.api(
    		//"/" + userId + "?access_token=" + access_token,
    		"/me/taggable_friends",
    		function (response) {
      			if (response && !response.error) {
        			console.log(response);
      			}
      			else{
      				console.log(response);
      			}
    		}
		);
	}, {scope : ['user_posts', 'user_friends']});


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







