
let count = 0

let gp = {
    fileLoaded: false,
}

function checkZip() {
    if (gp.zip === undefined || gp.zip === null) {
        alert('No level file uploaded');
        return false;
    }
    return true;
}

class Proc {
    constructor() {
        this.zip = null;
    }

    load(file) {
        // Load cytoidlevel file content
        return file.arrayBuffer()
            .then((content) => {
                let zip = new JSZip();
                return zip.loadAsync(content);
            })
    }

    getOldMusic() {
        // Get the music file to download to change speed
        this.zip.file("level.json")
            then((content) => {
                (content)
            })
    }
    setInfo(info) {
        // Set newly generated level informations
    }
    setNewMusic(content) {
        // Set uploaded new music file
    }
    export() {
        // Export the generated cytoidlevel file content to download
    }
}

function loadLevelFile() {
    let input = $("#cytlvl-file")[0];

    console.log(input.files[0]);
    // gp.d = input.files[0];
    return input.files[0].arrayBuffer()
        .then((content) => {
            let zip = new JSZip();
            return zip.loadAsync(content);
        })
}

$(document).ready(() => {
    // $("#cytlvl-file").on("input", () => {
    // });

    $("#btn-load-file").on("click", () => {
        console.log("load");

        let inputElem = $("#cytlvl-file")[0];

        if (inputElem.files.length < 1) {
            alert("No file selected")
            return;
        }    

        return inputElem.files[0].arrayBuffer()
            .then((content) => {
                gp.zipContent = content;
                let zip = new JSZip();
                return zip.loadAsync(content);
            })
            .then((zip) => {
                gp.zip = zip;
                return zip.file("level.json").async("string");
            })
            .then((content) => {
                let obj;
                try {
                    obj = JSON.parse(content)
                } catch (e) {
                    alert("Cannot parse level");
                    return;
                }

                gp.obj = obj;
            });

    });

    $("#btn-download-music").on("click", () => {
        if (!checkZip()) return;

        console.log("download music");
        
        let {zip, obj} = gp;

        function arraybuffer2blob(buffer) {
            return new Blob([new Uint8Array(buffer, 0, buffer.length)]);
        }

        let path = obj.music.path;
        zip.file(path).async('arraybuffer')
            .then((content) => {
                console.log(path);
                let ext = path.split('.').pop();
                saveAs(arraybuffer2blob(content), `music.${ext}`);
            })
    });

    $('#btn-export').on('click', () => {
        let {zip, obj} = gp;
        let out;
        let outObj;

        let input = $('#new-music')[0]
        if (input.files.length < 1) {
            alert('No music uploaded');
            throw 'error';
        }
        let newMusicFile = input.files[0];

        let musicPathZ = obj.music.path;

        loadLevelFile()
            .then((out_) => {
                out = out_;
                return newMusicFile.arrayBuffer()
            })
            .then((content) => {
                out.file(musicPathZ, content);

            })
    })

    $('#btn-test').on('click', () => {
    })

})

