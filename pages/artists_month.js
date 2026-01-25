fetch("../data.json")
            .then(response => response.json())
            .then(data => {

                const tbody = document.querySelector("#top-artists-month tbody");

                data.artists.month.forEach((artist, index) => {
                    const tr = document.createElement("tr");

                    tr.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${artist.name}</td>
                        <td>${artist.plays}</td>
                        <td>${artist.minutes.toFixed(1)}</td>
                        <td>${artist.percentageOfMinutes}%</td>
                    `;

                    tbody.appendChild(tr);
                });
            });