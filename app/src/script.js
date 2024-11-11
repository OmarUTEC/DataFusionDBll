const searchButton = document.getElementById('search-button');
searchButton.addEventListener('click', () => {
    const query = document.getElementById('query-input').value;
    const topk = document.getElementById('topk-input').value;
    const url = `/buscar?query=${query}&topk=${topk}`;
    const tablaResultados = document.getElementById('tabla-resultados').getElementsByTagName('tbody')[0];

    const xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            const response = JSON.parse(this.responseText);
            
            // Limpiar la tabla antes de agregar los resultados
            tablaResultados.innerHTML = '';

            // Llenar la tabla con los resultados de la búsqueda
            if (response) {
                Object.keys(response).forEach(key => {
                    const item = response[key];
                    const tr = document.createElement('tr');
                    
                    // Crear las celdas con los datos
                    const tdTrackId = document.createElement('td');
                    tdTrackId.textContent = item.track_id;
                    tr.appendChild(tdTrackId);
                    
                    const tdTrackName = document.createElement('td');
                    tdTrackName.textContent = item.track_name;
                    tr.appendChild(tdTrackName);
                    
                    const tdTrackArtist = document.createElement('td');
                    tdTrackArtist.textContent = item.track_artist;
                    tr.appendChild(tdTrackArtist);
                    
                    const tdLyrics = document.createElement('td');
                    tdLyrics.textContent = item.lyrics.length > 100 ? item.lyrics.substring(0, 100) + "..." : item.lyrics;
                    tr.appendChild(tdLyrics);
                    
                    const tdPopularity = document.createElement('td');
                    tdPopularity.textContent = item.track_popularity;
                    tr.appendChild(tdPopularity);
                    
                    const tdAlbumName = document.createElement('td');
                    tdAlbumName.textContent = item.track_album_name;
                    tr.appendChild(tdAlbumName);
                    
                    const tdAlbumReleaseDate = document.createElement('td');
                    tdAlbumReleaseDate.textContent = item.track_album_release_date;
                    tr.appendChild(tdAlbumReleaseDate);
                    
                    const tdPlaylistName = document.createElement('td');
                    tdPlaylistName.textContent = item.playlist_name;
                    tr.appendChild(tdPlaylistName);
                    
                    const tdPlaylistGenre = document.createElement('td');
                    tdPlaylistGenre.textContent = item.playlist_genre;
                    tr.appendChild(tdPlaylistGenre);
                    
                    const tdDanceability = document.createElement('td');
                    tdDanceability.textContent = item.danceability;
                    tr.appendChild(tdDanceability);
                    
                    const tdEnergy = document.createElement('td');
                    tdEnergy.textContent = item.energy;
                    tr.appendChild(tdEnergy);
                    
                    const tdTempo = document.createElement('td');
                    tdTempo.textContent = item.tempo;
                    tr.appendChild(tdTempo);

                    // Agregar la fila a la tabla
                    tablaResultados.appendChild(tr);
                });
            }
        }
    };

    xhr.open('GET', url, true);
    xhr.send();
});
