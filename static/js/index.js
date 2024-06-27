
$('#searchBtn').click(function() {
    const malUsername = $('#malUsername').val();
    const mangaSearch = $('#mangaSearch').val();
    // Example API call: replace with your actual API URL and parameters
    apiUrl = "";
    if (malUsername != ""){
        apiUrl = `https://ian.ibalton.com/api/recommendations/user/${malUsername}`;
    } else {
        apiUrl = `https://ian.ibalton.com/api/recommendations/manga/${mangaSearch}`;
    }
    $('#mangaContainer').empty();
    console.log(apiUrl);
    $.ajax({
        url: apiUrl,
        type: 'get',
        contentType: 'application/json; charset=utf-8',
        success: function(data) {

            console.log("building container");
            // Your success code here
            if (data["res"].length > 0) {
                data["res"].forEach((manga, index) => {
                    

                    
                    $('#mangaContainer').append(`
                        <div class="col-md-4 mb-4">
                            <div class="card bg-secondary text-light manga-card">
                                <img src="${manga.thumbnail}" class="card-img-top" alt="Manga Image Placeholder">
                                <div class="card-body">
                                    <h5 class="card-title">${manga.title}</h5>
                                    <p class="card-text">Recommended Order: ${index + 1}</p>
                                    <div class="synopsis">${manga.synopsis}</div>
                                </div>
                            </div>
                        </div>
                    `);
                    if(manga.thumbnail == undefined || manga.thumbnail == "null"){
                    getMangaThumbnail(manga.manga_id,index)}
                });
            } else {
                $('#mangaContainer').append('<div class="col">No mangas found.</div>');
            }
        },
        error: function(xhr, status, error) {
            console.error("Error: " + status + " " + error);
        }
    });
  
});

async function getMangaThumbnail(mangaId,index){
    
    try {
        imgURl = "";
        await $.ajax({
            url:`https://ian.ibalton.com/api/manga-thumbnail/${mangaId}` ,
            type: 'get',
            contentType: 'application/json; charset=utf-8',
            success: function(data) {
                imgURl = data.res

            },
            error: function(xhr, status, error) {
                console.error("Error: " + status + " " + error);
            }
        });
        // Log or return the src attribute


        // Access the #mangaContainer element and find the img element at the specified index
        const mangaContainer = document.querySelector('#mangaContainer');
        const imgs = mangaContainer.querySelectorAll('img');

       
        imgWidget = imgs[index];
        imgWidget.src = imgURl; // Update the src attribute of the img element
       

        return imgURl;
      } catch (error) {
        console.error('Error fetching manga thumbnail:', error);
        return null;
      }
}
