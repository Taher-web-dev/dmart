export default async function custom_fetch(url, request) {
		let response = await fetch(url, request); 
		return await response.json();
}

