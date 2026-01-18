fetch("data.json")
    .then(respone => Response.json())
    .then(data => {
        console.log(data);
    });