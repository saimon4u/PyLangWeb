async function getOutput(){ 
    const code = document.getElementById('code_area').value

    response = await fetch('/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
    });

    const val = await response.json()

    data = val.data
    const outputDiv = document.getElementById('p_tag');
    outputDiv.innerText = data;
} 


document.getElementById('code_area').addEventListener('input', ()=>{
    document.getElementById('p_tag').innerText = null
})



function clearScreen(){
    const box = document.getElementById('code_area')

    box.value = null

    const terminal = document.getElementById('p_tag')

    terminal.textContent = null

}


document.getElementById('code_area').onkeydown = function(e) {
    if (e.keyCode === 9) {
        this.setRangeText(

            '    ',

            this.selectionStart,

            this.selectionStart,

            'end'

        )

        return false;
    }
};