
$('signup').on('submit', function(event) {
	event.preventDefault();

	var $form = $(this),
		username = $form.find("input[name='username']"),
		password = $form.find("input[name='password']"),
		email = $form.find("input[name='email']");

	$ajax({
		method: 'POST',
		url: 'http://localhost:5000/users',
		data: {username: username, password: password, email: email}});
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
