import sharp from 'sharp'
import fs from 'fs'

const svgBuffer = fs.readFileSync('./public/icons/tree-marker.svg')
sharp(svgBuffer)
    .png()
    .toFile('./public/icons/tree-marker.png')
    .then(() => console.log('Ícone convertido com sucesso!'))
    .catch(err => console.error('Erro ao converter ícone:', err)) 