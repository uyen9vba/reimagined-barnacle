
document.getElementById('home').setAttribute('href', 'https://localhost:5000/')

const serialize_form = form => JSON.stringify(
	Array.from(new FormData(form).entries()).reduce(
		(m, [key, value]) => Object.assign(m, {[key]: value}), {})
);

$('signup').on('submit', function(event) {
	event.preventDefault();
	const json = serialize_form(this);
	console.log(json);
});


