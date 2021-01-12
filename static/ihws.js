
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
			console.log(response)
			window.location.replace('/');
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
			window.location.replace('/');
		});
	});

	$('#delete').click(function(event) {
		event.preventDefault();

		var uuid = window.location.pathname.split('/');

		$.ajax({
			type: 'DELETE',
			url: 'http://localhost:5000/images/' + uuid[2],
			headers: {'Authorization': 'Bearer ' + access_token}
		}).done(function(response) {
			console.log(response);
			window.location.replace('/images');
		});
	});

	$(document).on('click', '#patch-image', function(event) {
		event.preventDefault();

		var uuid = window.location.pathname.split('/');

		var tags = $('#tags > p');
		console.log(tags);
		var json_tags = [];

		for (var a = 0; a < tags.length; a++) {
			json_tags.push(tags[a].innerHTML);
		}

		var data = JSON.stringify({
			'name': document.getElementById('name').innerHTML,
			'description': document.getElementById('description').innerHTML,
			'private': document.getElementById('private').checked,
			'tags': json_tags});

		console.log(json_tags);

		$.ajax({
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json',
				'Authorization': 'Bearer ' + access_token},
			type: 'PATCH',
			url: 'http://localhost:5000/images/' + uuid[2],
			dataType: 'json',
			data: data
		}).done(function(response) {
			console.log(response);
			location.reload();
		});
	});

	$(document).on('click', '#edit', function(event) {
		event.preventDefault();

		$('.edit').attr('contenteditable', 'true');
		$('.edit').attr('style', 'background-color: #D0E8F2; border-radius: 10px;');

		var patchButton = $('#edit').clone();
		patchButton.attr('value', 'Save');
		patchButton.appendTo('#buttons');

		document.getElementById('edit').remove();

		var cancelButton = $('#delete').clone();
		cancelButton.attr('value', 'Cancel');
		cancelButton.attr('id', 'cancel');
		cancelButton.appendTo('#buttons');

		if (window.location.href == 'http://localhost:5000/profile') {
			patchButton.attr('id', 'patch-profile');
		}
		else {
			patchButton.attr('id', 'patch-image');

			$('<input id="private" type="checkbox" style="float: right; margin-left: 4px">').appendTo('#privatebutton');
			$('<label id="privatelabel" style="display: inline; float: right">Private</label>').appendTo('#privatebutton');

			$('<input id="add-tag" type="button" value="Add tag">').prependTo('#tag-div');
			$('<input id="tag" type="text">').prependTo('#tag-div');
			$('<label id="tag-label">Tags</label></br>').prependTo('#tag-div');
		}
	});

	$(document).on('click', '#cancel', function() {
		$('.edit').attr('contenteditable', 'false');
		$('.edit').attr('style', 'background-color: #FFF;');

		document.getElementById('cancel').remove();

		if (window.location.href == 'http://localhost:5000/profile') {
			var editButton = $('#patch-profile').clone();
			editButton.attr('value', 'Edit');
			editButton.attr('id', 'edit');
			editButton.appendTo('#buttons');

			document.getElementById('patch-profile').remove();
		}
		else {
			var editButton = $('#patch-image').clone();
			editButton.attr('value', 'Edit');
			editButton.attr('id', 'edit');
			editButton.appendTo('#buttons');

			document.getElementById('patch-image').remove();

			document.getElementById('private').remove();
			document.getElementById('privatelabel').remove();
			document.getElementById('tag-label').remove();
			document.getElementById('tag').remove();
			document.getElementById('add-tag').remove();
		}
	});

	$(document).on('click', '#revoke', function() {
		$.ajax({
			url: 'http://localhost:5000/revoke',
			type: 'POST',
			headers: {'Authorization': 'Bearer ' + access_token}
		}).done(function(response) {
			console.log(response);
			window.location.replace('/');
		});
	});

	$('#upload').submit(function(event) {
		event.preventDefault();

		var formData = new FormData();
		
		formData.append('name', $('input[name=name]').val());
		formData.append('description', document.getElementById('description').value);
		formData.append('file', $('#file')[0].files[0]);
		formData.append('private', document.getElementById('private').checked);

		var tags = $('#tags > p');
		console.log(tags);
		var json_tags = [];

		for (var a = 0; a < tags.length; a++) {
			json_tags.push(tags[a].innerHTML);
		}
		formData.append('tags', json_tags);
		console.log(json_tags);
		
		$.ajax({
			url: 'http://localhost:5000/images',
			type: 'POST',
			headers: {'Authorization': 'Bearer ' + access_token},
			data: formData,
			mimeType: 'multipart/form-data',
			enctype: 'multipart/form-data',
			contentType: false,
			processData: false
		}).done(function(response) {
			var json = $.parseJSON(response);
			console.log(json);
			window.location.replace('http://localhost:5000/images/' + json['uuid']);
		});
	});

	$(document).on('click', '#patch-profile', function(event) {
		event.preventDefault;

		var formData = new FormData();
		console.log(document.getElementById('username').value);

		formData.append('username', document.getElementById('username').value);
		formData.append('email', document.getElementById('email').value);
		formData.append('file', $('#file')[0].files[0]);

		console.log(formData);

		$.ajax({
			url: 'http://localhost:5000/user',
			type: 'PATCH',
			headers: {'Authorization': 'Bearer ' + access_token},
			data: formData, 
			mimeType: 'multipart/form-data',
			enctype: 'multipart/form-data',
			contentType: false,
			processData: false
		}).done(function(response) {
			console.log(response);
			window.location.replace('/');
		});
	});

	$(document).on('click', '#add-tag', function() {
		var tag = $('<p id="delete-tag" class="tag"></p>');
		tag.text($('#tag').val());
		tag.prependTo('#tags');
		$('#tag').text('');
	});

	$(document).on('click', '#delete-tag', function() {
		$(this).remove();
	});
});
