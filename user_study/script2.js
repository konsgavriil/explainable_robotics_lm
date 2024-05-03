function generateLatinSquare(n) {
    let latinSquare = [];
    const remainder = n % 3;
    switch (remainder) {
        case 0:
            latinSquare = [1, 2, 3];
            break;
        case 1:
            latinSquare = [2, 3, 1];
            break;
        case 2:
            latinSquare = [3, 1, 2];
            break;
        default:
            console.log("Not implemented.");
    }
    return latinSquare;
}

// Example usage:
const n = 2; // Change n to change the size of the Latin square
const seq = generateLatinSquare(n);
console.log(seq);
