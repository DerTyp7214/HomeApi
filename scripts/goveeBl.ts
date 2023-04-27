import noble from 'noble-winrt'

const MODEL_NUMBER_UUID = '00002a24-0000-1000-8000-00805f9b34fb'

noble.on('discover', (peripheral) => {
  if (peripheral.advertisement.localName?.startsWith('ihome') == true) {
    console.log(`Found ${peripheral.advertisement.localName}`)
    peripheral.discoverServices(
      ['000102030405060708090a0b0c0d1910'],
      (err, services) => {
        console.log(`Found ${services.length} services`)
        console.log(err)
      }
    )
  }
})

if (noble.state === 'poweredOn') noble.startScanning()

noble.on('stateChange', (state) => {
  if (state === 'poweredOn') noble.startScanning()
  else noble.stopScanning()
})
