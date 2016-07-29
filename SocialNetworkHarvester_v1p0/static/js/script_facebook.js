window.fbAsyncInit = function() {
	FB.init({
		appId	: '1113358652058016',
		xfbml	: true,
		version	: 'v2.6'
	});

	console.log('Api loaded');

	FB.login(function(response){
		console.log(response);
	});
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

$(document).ready(function() {
    
    
});







