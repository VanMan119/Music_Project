fetch("data.json")
    .then(respone => response.json())
    .then(data => {
        console.log(data);
    });