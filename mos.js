Array.prototype.shuffle = function () {
    var i = this.length;
    while (i) {
        var j = Math.floor(Math.random() * i);
        var t = this[--i];
        this[i] = this[j];
        this[j] = t;
    }
    return this;
}

// invalid enter key
function invalid_enter() {
    if (window.event.keyCode == 13) {
        return false;
    }
}

// start experiment
function start_experiment() {
    // ユーザ名の取得（空白はアンダースコアに変換）
    var name = document.getElementById("name").value.trim().replace(/ /g, "_");
    if (name === "") {
        alert("Please enter your name.");
        return false;
    }

    // set番号の取得
    var set_num = "";
    var set_elements = document.getElementsByName("set");
    for (var i = 0; i < set_elements.length; i++) {
        if (set_elements[i].checked) {
            set_num = set_elements[i].value;
            break;
        }
    }
    if (set_num === "") {
        alert("Please select a set number.");
        return false;
    }

    // multiplier（A, B, C）の取得
    var multiplier = "";
    var mult_elements = document.getElementsByName("multiplier");
    for (var i = 0; i < mult_elements.length; i++) {
        if (mult_elements[i].checked) {
            multiplier = mult_elements[i].value;
            break;
        }
    }
    if (multiplier === "") {
        alert("Please select a multiplier option (A, B, or C).");
        return false;
    }

    // 表示切替
    Display();

    // ベースディレクトリ（wav/直下）
    const wav_dir = "wav/";
    // 対象setのベースパス
    var base_path = wav_dir + "set" + set_num + "/";
    // 各セットは表面的には、set{set_num}_{multiplier} となる
    // 再生用のディレクトリは、選択されたmultiplierに対応
    var effective_dir = "";
    if (multiplier === "A") {
        effective_dir = base_path + "f0.50/";
    } else if (multiplier === "B") {
        effective_dir = base_path + "f1.00/";
    } else if (multiplier === "C") {
        effective_dir = base_path + "f2.00/";
    }

    // 但し、B (f1.00) の場合は Natural.list も使い、A (f0.50) および C (f2.00) の場合は Natural.list を除外する
    var method_paths = [];
    if (multiplier === "B") {
        method_paths.push(base_path + "f1.00/Natural.list");
        method_paths.push(base_path + "f1.00/SiFiGAN.list");
        method_paths.push(base_path + "f1.00/VAE-SiFiGAN.list");
        method_paths.push(base_path + "f1.00/wo_prior.list");
    } else if (multiplier === "A") {
        method_paths.push(base_path + "f0.50/SiFiGAN.list");
        method_paths.push(base_path + "f0.50/VAE-SiFiGAN.list");
        method_paths.push(base_path + "f0.50/wo_prior.list");
    } else if (multiplier === "C") {
        method_paths.push(base_path + "f2.00/SiFiGAN.list");
        method_paths.push(base_path + "f2.00/VAE-SiFiGAN.list");
        method_paths.push(base_path + "f2.00/wo_prior.list");
    }

    // ファイルリストの作成
    file_list = makeFileList(method_paths);
    // 出力CSVのファイル名を、名前_set{set_num}_{multiplier}.csv とする
    outfile = name + "_set" + set_num + "_" + multiplier + ".csv";
    // 評価スコア初期化
    scores = (new Array(file_list.length)).fill(0);
    // 評価用ラジオボタンの要素
    eval_buttons = document.getElementsByName("eval");
    // 初期化
    init();
}

// 表示切替
function Display() {
    document.getElementById("Display1").style.display = "none";
    document.getElementById("Display2").style.display = "block";
}

// テキストファイル読み込み
function loadText(filename) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", filename, false);
    xhr.send(null);
    var list = xhr.responseText.split(/\r\n|\r|\n/);
    // 空行除去
    if (list[list.length - 1] === "") {
        list.pop();
    }
    return list;
}

// ファイルリスト作成：各リストファイルの内容を結合し、シャッフルする
function makeFileList(method_paths) {
    var files = [];
    for (var i = 0; i < method_paths.length; i++) {
        var tmp = loadText(method_paths[i]);
        files = files.concat(tmp);
    }
    files.shuffle();
    return files;
}

function setAudio() {
    document.getElementById("page").textContent = (n + 1) + "/" + scores.length;
    document.getElementById("audio").innerHTML = 'Voice:<br>' +
        '<audio src="' + file_list[n] + '" controls preload="auto">' +
        '</audio>';
}

function init() {
    n = 0;
    setAudio();
    evalCheck();
    setButton();
}

function evalCheck() {
    if (scores[n] <= 0 || scores[n] > eval_buttons.length) {
        for (var i = 0; i < eval_buttons.length; i++) {
            eval_buttons[i].checked = false;
        }
    } else {
        eval_buttons[5 - scores[n]].checked = true;
    }
}

function setButton() {
    if (n === (scores.length - 1)) {
        document.getElementById("prev").disabled = false;
        document.getElementById("next2").disabled = true;
        document.getElementById("finish").disabled = true;
        for (var i = 0; i < eval_buttons.length; i++) {
            if (eval_buttons[i].checked) {
                document.getElementById("finish").disabled = false;
                break;
            }
        }
    } else {
        document.getElementById("prev").disabled = (n === 0);
        document.getElementById("next2").disabled = true;
        document.getElementById("finish").disabled = true;
        for (var i = 0; i < eval_buttons.length; i++) {
            if (eval_buttons[i].checked) {
                document.getElementById("next2").disabled = false;
                break;
            }
        }
    }
}

function evaluation() {
    for (var i = 0; i < eval_buttons.length; i++) {
        if (eval_buttons[i].checked) {
            scores[n] = 5 - i;
        }
    }
    setButton();
}

function exportCSV() {
    var csvData = "";
    for (var i = 0; i < file_list.length; i++) {
        csvData += file_list[i] + "," + scores[i] + "\r\n";
    }
    var link = document.createElement("a");
    document.body.appendChild(link);
    link.style.display = "none";
    var blob = new Blob([csvData], { type: "octet/stream" });
    var url = window.URL.createObjectURL(blob);
    link.href = url;
    link.download = outfile;
    link.click();
    window.URL.revokeObjectURL(url);
    link.parentNode.removeChild(link);
}

function next() {
    n++;
    setAudio();
    evalCheck();
    setButton();
}

function prev() {
    n--;
    setAudio();
    evalCheck();
    setButton();
}

function finish() {
    exportCSV();
}

// directory name（wav/直下）
const wav_dir = "wav/";

// invalid enter key
document.onkeypress = invalid_enter();

// グローバル変数
var outfile;
var file_list;
var scores;
var n = 0;
var eval_buttons = document.getElementsByName("eval");
