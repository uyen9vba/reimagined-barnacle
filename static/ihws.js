
$(document).ready(function() {
	$('#signup').submit(function(event) {
		event.preventDefault();

		var data = JSON.stringify({
			'email': $('input[name=email]').val(),
			'username': $('input[name=username]').val(),
			'password': $('input[name=password]').val()});

		$.ajax({
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json'},
			url: 'http://localhost:5000/users',
			type: 'POST',
			dataType: 'json',
			data: data
		}).done(function(response) {
			console.log(response);
		});
	});

	$('#signin').submit(function(event) {
		event.preventDefault();

		var data = JSON.stringify({
			'email': $('input[name=email]').val(),
			'password': $('input[name=password]').val()});

		$.ajax({
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json'},
			url: 'http://localhost:5000/token',
			type: 'POST',
			dataType: 'json',
			data: data
		}).done(function(response) {
			console.log(response);
		});
	});

	$('#delete').click(function(event) {
		event.preventDefault();

		var filename = window.location.pathname.split('/');

		$.ajax({
			type: 'DELETE',
			url: 'http://localhost:5000/images/' + filename[1]});
			
	});

	$('#upload').submit(function(event) {
		event.preventDefault();

		var formData = new FormData();
		
		formData.append('name', $('input[name=name]').val());
		formData.append('description', document.getElementById('description').value);
		formData.append('file', $('#file')[0].files[0]);
		
		$.ajax({
			url: 'http://localhost:5000/images',
			type: 'POST',
			data: formData,
			mimeType: 'multipart/form-data',
			enctype: 'multipart/form-data',
			contentType: false,
			processData: false
		}).done(function(response) {
			console.log(response);
		});
	});
});
