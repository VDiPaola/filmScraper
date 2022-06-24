$.getJSON("./movieData.json")
.done(function( data ) {
const perPage = 10;
const titles = Object.keys(data);

let maxPages = Math.ceil(titles.length /perPage);
let filteredTitles = titles;
let curPage = 0;

const pagination = document.getElementsByClassName("pagination")[0];
const table = document.getElementById("table");

const search = document.getElementById("search");
document.getElementById("searchButton").addEventListener("click", (e)=>{
    let val = search.value;
    //get value
    if(val){
        filteredTitles = titles.filter(title => title.toLowerCase().includes(val.toLowerCase()))
    }else{
        filteredTitles = titles;
    }
    //update table

    //update pagination
    maxPages = Math.ceil(filteredTitles.length /10);
    updatePagination();
})

document.getElementById("prev").addEventListener("click", (e)=>{
    curPage = curPage <= 0 ? 0 : curPage-1
    updateTable();
})

document.getElementById("next").addEventListener("click", (e)=>{
    curPage = curPage >= maxPages-1 ? maxPages-1 : curPage+1
    updateTable();
})

function updateTable(){
    table.innerHTML = ""

    let offsetIndex = curPage * perPage;
    let pageTitles = filteredTitles.slice(offsetIndex, offsetIndex+perPage)
    for(let i=0;i<pageTitles.length;i++){
        createTableEl(pageTitles[i], data[pageTitles[i]])
    }
}

function createTableEl(text, hash){
    const li = document.createElement("li");
    li.classList.add("list-group-item");
    li.innerText = text;
    table.appendChild(li)

    li.addEventListener("click", (_)=>{
        navigator.clipboard.writeText(hash);
        $("#copyAlert").show();
        $("#copyAlert").delay(2000).hide(0);
    })
}

updateTable();

});