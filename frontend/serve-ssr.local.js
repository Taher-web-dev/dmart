const express = require('express');
const { ssr } = require('@sveltech/ssr');
const path = require('path');

const port = 4040;
const static_dir= path.resolve("./dist/");
const app = express();

app.use(express.static(static_dir));
app.get('*', serve_ssr); 
console.log(`Serving ${static_dir} on port ${port}`);
app.listen(port);

async function serve_ssr(req, res) {
		const bundle = path.resolve(`./dist/build/bundle.js`);
		const entrypoint = path.resolve(`./dist/__app.html`);
		const host = `http://${req.hostname}`;
		const url = req.url;
		//console.log(`Requested ... ${host}${url}`);
		var out = "hi there\n"; 
		try {
				  out = await ssr(entrypoint, bundle, url, {host});
				} catch (ex) {
							console.log("Something went wrong", ex);
							out = "nothing to say\n";
						}
		res.send(out);
}
