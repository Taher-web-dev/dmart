const express = require('express');
const { ssr } = require('@roxi/ssr');
const path = require('path');

const port = 4040;
const static_dir= path.resolve("../run/public/");
const app = express();

app.use(express.static(static_dir));
app.get('*', serve_ssr); 
console.log(`Serving ${static_dir} on port ${port}`);
app.listen(port);

async function serve_ssr(req, res) {
		 let decoded_url = req.url // decodeURIComponent(req.url);
		 let split = decoded_url.split('/');
		 const space = split[1];
		 const bundle = path.resolve(`../run/public/${space}/build/bundle.js`);
		 const entrypoint = path.resolve(`../run/public/${space}/__app.html`);
		 const host = `http://${req.hostname}`;
		 split[1] = ""; // A trick for the join below
		 const url = split.slice(1).join('/');
		 //console.log(`Before ... ${host} ...${url} ...  ${space}`);
		 var out = ""; 

		 if(url.endsWith(".js") || url.endsWith(".css") || url.endsWith(".png") || url.endsWith(".xml")){
			 console.log("A resource was requested by mistake: ", url);
			 res.send("");
			 return;
		 }
		 try {
			 		console.log("In app: ", host + url)
		 		  out = await ssr(entrypoint, bundle, url, {host});
		 		} catch (ex) {
		 					console.log("Something went wrong", ex);
		 					out = "nothing to say\n";
		 				}
		 res.send(out);
}
