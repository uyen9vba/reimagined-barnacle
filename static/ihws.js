
$('signup').on('submit', function(event) {
	event.preventDefault();

	var $form = $(this),
		username = $form.find("input[name='username']"),
		password = $form.find("input[name='password']"),
		email = $form.find("input[name='email']");

	$ajax({
		url: 'http://localhost:5000/users',
		method: 'POST',
		timeout: 0,
		data: {"username": username, "password": password, "email": email}
	});
});

$('signin').on('submit', function(event) {
	event.preventDefault();

	email = document.getElementById('email').value;
	password = document.getElementById('password').value;

	alert('done');

	var settings = {
		url: 'http://localhost:5000/token',
		method: 'POST',
		timeout: 0,
		data: {"email": email, "password": password}};

	request = $.ajax(settings);

	request.done(function(msg) {
		alert('Done');
	});

});

$('upload').submit(function(event) {
	event.preventDefault();

	var $form = $(this),
		file = $form.find("input[name='file']"),
		name = $form.find("input[name='name']").val(),
		description = $form.find("input[name='description']").val();
	
	var result = $ajax({
		method: 'POST',
		url: 'http://localhost:5000/images',
		data: {name: name, description: description},
		dataType: 'json'});

	$ajax({
		method: 'PUT',
		url: 'http://localhost:5000/images/' + result.id + '/cover',
		data: new FormData(file)});
});
