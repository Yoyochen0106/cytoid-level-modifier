
let count = 0

let gp = {
    fileLoaded: false,
}

function checkZip() {
    return true;
}

$(document).ready(() => {
    // $("#cytlvl-file").on("input", () => {
    // });

    $("#btn-load-file").on("click", () => {
        console.log("load");
        let input = $("#cytlvl-file")[0];
        if (input.files.length >= 1) {
            let fReader = new FileReader();
            console.log(input.files[0]);
            // gp.d = input.files[0];
            fReader.readAsArrayBuffer(input.files[0]);
            fReader.onloadend = (event) => {
                let data = event.target.result;
                let zip = new JSZip();
                zip.loadAsync(data)
                    .then((zip) => {
                        gp.zip = zip;
                    });
            };
        } else {
            alert("No file selected")
        }
    });

    $("#btn-download-music").on("click", () => {
        if (!checkZip()) return;

        console.log("download music");
        
        let {zip} = gp;

        zip.file("level.json").async("string").then((content) => {
            let obj;
            try {
                obj = JSON.parse(content)
            } catch (e) {
                alert("Cannot parse level");
                return;
            }

            function arraybuffer2blob(buffer) {
                return new Blob([new Uint8Array(buffer, 0, buffer.length)]);
            }

            let path = obj.music.path;
            console.log(path);
            zip.file(path).async('arraybuffer')
                .then((content) => {
                    console.log(path);
                    let ext = path.split('.').pop();
                    saveAs(arraybuffer2blob(content), `music.${ext}`);
                })

            gp.obj = obj;
        })
    });

})

