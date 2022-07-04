function closest(num, arr) {
    const diffArr = arr.map(x => Math.abs(num - x));
    const minNumber = Math.min(...diffArr);
    const index = diffArr.findIndex(x => x === minNumber);
    return index;
}


function table_to_csv(source,zmin_id,zmax_id,rmin_id, rmax_id) {
    var columns = Object.keys(source.data)
    columns.pop()
    const nrows = source.get_length()
    const lines = []

    for (let i = rmin_id; i < rmax_id; i++) {
        let row = [];
        for (let j = 0; j < columns.length; j++) {
            const column = columns[j]
            //row.push(source.data[column][i].toString())
            var arr = source.data[column][i].toString().split('\t')
            for (let k=zmin_id; k < zmax_id; k++){
                row.push(arr[k])
            }
            //row.push(string[0])
        }
        lines.push(row.join('\t'))
    }
    return lines.join('\n').concat('\n')
}


const filename = data[sl.value].toFixed(3).toString().concat('s_data_'+file).concat('.txt')
//const filename = 'output.txt'
var index = sl.value - 1
var zmin_id = closest(sl_zmin.value, znew)
var zmax_id = closest(sl_zmax.value, znew)
var rmin_id = closest(sl_rmin.value, rnew)
var rmax_id = closest(sl_rmax.value, rnew)

var filetext = table_to_csv(source[index],zmin_id,zmax_id,rmin_id, rmax_id)
if (file == 'Ne'){
filetext = '2D_ne\nR '.concat(sl_rmin.value.toFixed(3)+' '+sl_rmax.value.toFixed(3)).concat('\nZ ' +sl_zmin.value.toFixed(3) +' '+sl_zmax.value.toFixed(3)+'\n').concat(filetext)
} else {
filetext = '2D_Te\nR '.concat(sl_rmin.value.toFixed(3)+' '+sl_rmax.value.toFixed(3)).concat('\nZ ' +sl_zmin.value.toFixed(3) +' '+sl_zmax.value.toFixed(3)+'\n').concat(filetext)
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