document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const tablaAContainer = document.getElementById('tablaA-container');
    const tablaBContainer = document.getElementById('tablaB-container');
    const tablaABody = document.getElementById('tablaA-body');
    const tablaBBody = document.getElementById('tablaB-body');
    const tiempoConsultaSpan = document.getElementById('tiempo_consulta');

    // Evento para la búsqueda
    searchForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Evitar el envío tradicional del formulario

        const consulta = document.getElementById('searchQuery').value.trim();
        const top_k = parseInt(document.getElementById('topk').value);

        if (consulta === '' || isNaN(top_k) || top_k < 1) {
            alert('Por favor, ingresa una consulta válida y un Top K válido.');
            return;
        }

        // Limpiar resultados anteriores
        tablaABody.innerHTML = '';
        tablaBBody.innerHTML = '';
        tablaAContainer.style.display = 'none';
        tablaBContainer.style.display = 'none';
        tiempoConsultaSpan.textContent = '0';

        // Registrar el tiempo de inicio
        const startTime = performance.now();

        // Verificar cuál tabla se seleccionó y enviar la solicitud correspondiente
        const selectedTable = document.querySelector('.active').id; // 'tablaA' o 'tablaB'

        let endpoint = '/consulta'; // Por defecto se utiliza '/consulta' para la tabla A
        if (selectedTable === 'tablaB') {
            endpoint = '/consulta_db'; // Cambiar a '/consulta_db' para la tabla B
        }

        // Enviar la solicitud al back-end usando Fetch API
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ consulta: consulta, top_k: top_k })
        })
        .then(response => response.json())
        .then(data => {
            // Calcular el tiempo de ejecución
            const endTime = performance.now();
            const tiempoEjecucion = ((endTime - startTime) / 1000).toFixed(3);
            tiempoConsultaSpan.textContent = tiempoEjecucion;

            // Verificar si hay resultados
            if (Object.keys(data).length === 0) {
                if (selectedTable === 'tablaA') {
                    tablaABody.innerHTML = '<tr><td colspan="21">No se encontraron resultados.</td></tr>';
                } else {
                    tablaBBody.innerHTML = '<tr><td colspan="15">No se encontraron resultados.</td></tr>';
                }
            } else {
                // Insertar cada resultado en la tabla correspondiente
                for (const id in data) {
                    const doc = data[id];
                    const row = document.createElement('tr');

                    if (selectedTable === 'tablaA') {
                        // Crear y añadir celdas a la fila para tablaA
                        row.innerHTML = `
                            <td>${doc.track_id || 'N/A'}</td>
                            <td>${doc.track_name || 'N/A'}</td>
                            <td>${doc.track_artist || 'N/A'}</td>
                            <td>${doc.track_popularity || 'N/A'}</td>
                            <td>${doc.track_album_name || 'N/A'}</td>
                            <td>${doc.track_album_release_date || 'N/A'}</td>
                            <td>${doc.playlist_name || 'N/A'}</td>
                            <td>${doc.playlist_genre || 'N/A'}</td>
                            <td>${doc.playlist_subgenre || 'N/A'}</td>
                            <td>${doc.danceability || 'N/A'}</td>
                            <td>${doc.energy || 'N/A'}</td>
                            <td>${doc.key || 'N/A'}</td>
                            <td>${doc.loudness || 'N/A'}</td>
                            <td>${doc.mode || 'N/A'}</td>
                            <td>${doc.speechiness || 'N/A'}</td>
                            <td>${doc.acousticness || 'N/A'}</td>
                            <td>${doc.instrumentalness || 'N/A'}</td>
                            <td>${doc.liveness || 'N/A'}</td>
                            <td>${doc.valence || 'N/A'}</td>
                            <td>${doc.tempo || 'N/A'}</td>
                            <td>${doc.duration_ms || 'N/A'}</td>
                            <td>${doc.language || 'N/A'}</td>
                            <td>${doc.similitud_coseno || '0.0'}</td>
                        `;
                        tablaABody.appendChild(row);
                    } else {
                        // Crear y añadir celdas a la fila para tablaB (suponiendo estructura diferente)
                        row.innerHTML = `
                            <td>${doc.track_id || 'N/A'}</td>
                            <td>${doc.track_name || 'N/A'}</td>
                            <td>${doc.track_artist || 'N/A'}</td>
                            <td>${doc.track_popularity || 'N/A'}</td>
                            <td>${doc.track_album_name || 'N/A'}</td>
                        `;
                        tablaBBody.appendChild(row);
                    }
                }
            }

            // Mostrar el contenedor de resultados correspondiente
            if (selectedTable === 'tablaA') {
                tablaAContainer.style.display = 'block';
            } else {
                tablaBContainer.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error al realizar la búsqueda:', error);
            alert('Ocurrió un error al realizar la búsqueda. Por favor, intenta nuevamente.');
        });
    });

    // Funciones para manejar la selección de tablas
    function seleccionarTabla(tablaId) {
        if (tablaId === 'tablaA') {
            tablaAContainer.style.display = 'block';
            tablaBContainer.style.display = 'none';
        } else if (tablaId === 'tablaB') {
            tablaAContainer.style.display = 'none';
            tablaBContainer.style.display = 'block';
        }

        // Manejar la clase 'active' para los botones
        const botones = ['tablaA', 'tablaB'];
        botones.forEach(id => {
            document.getElementById(id).classList.toggle('active', id === tablaId);
        });
    }

    // Agregar eventos de clic a los botones para cambiar de tabla
    document.getElementById('tablaA').addEventListener('click', function() {
        seleccionarTabla('tablaA');
    });

    document.getElementById('tablaB').addEventListener('click', function() {
        seleccionarTabla('tablaB');
    });

    // Inicializar tabla por defecto
    seleccionarTabla('tablaA');
});
