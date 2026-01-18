fetch("../data.json")
    .then(response => response.json())
    .then(data => {
        console.log(data);

        const list = document.getElementById("top-artists-week");

        data.artists.lastWeek.forEach(artist => {
            const li = document.createElement("li");

            li.textContent = `${artist.name} - ${artist.minutes.toFixed(1)} min (${artist.plays} plays), ${artist.percentageOfMinutes}%`;

            list.appendChild(li);
        })
    });