function table_to_csv(source) {
    var columns = Object.keys(source.data)
    columns.pop()
    const nrows = source.get_length()
    const lines = [columns.join(',')]

    for (let i = 0; i < nrows; i++) {
        let row = [];
        for (let j = 0; j < columns.length; j++) {
            const column = columns[j]
            row.push(source.data[column][i].toString())
        }
        lines.push(row.join(','))
    }
    return lines.join('\n').concat('\n')
}


const filename = data[sl.value].toFixed(3).toString().concat('s_data_'+file).concat('.txt')
//const filename = 'output.txt'
var index = sl.value - 1
var filetext = table_to_csv(source[index])
if (file == 'Ne'){
filetext = '2D_ne\nR 0.611 1.107\nZ -0.508 0.508\n'.concat(filetext)
} else {
filetext = '2D_Te\nR 0.611 1.107\nZ -0.508 0.508\n'.concat(filetext)
}
const blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' })

//addresses IE
if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, filename)
} else {
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.target = '_blank'
    link.style.visibility = 'hidden'
    link.dispatchEvent(new MouseEvent('click'))
}