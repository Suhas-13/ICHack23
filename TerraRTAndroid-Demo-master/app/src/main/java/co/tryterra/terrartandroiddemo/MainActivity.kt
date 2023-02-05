package co.tryterra.terrartandroiddemo

import android.annotation.SuppressLint
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.Switch
import androidx.annotation.RequiresApi
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.res.ResourcesCompat
import co.tryterra.terrartandroid.TerraRT
import co.tryterra.terrartandroid.enums.Connections
import co.tryterra.terrartandroid.enums.DataTypes
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInOptions


@SuppressLint("UseSwitchCompatOrMaterialCode")
class MainActivity : AppCompatActivity(){
    private lateinit var terraRT: TerraRT
    @SuppressLint("SetTextI18n")
    @RequiresApi(Build.VERSION_CODES.O)

    private lateinit var bleConnect: Button
    private lateinit var wearOSButton: Button
    private lateinit var sensorButton: Button
    private lateinit var antButton: Button


    private var bleConnected: Boolean = false
    private var wearOsConnected: Boolean = false
    private var sensorConnected: Boolean = false
    private var antConnected: Boolean = false

    private lateinit var wearOsSwitch: Switch
    private lateinit var bleSwitch: Switch
    private lateinit var sensorSwitch: Switch
    private lateinit var antSwitch: Switch

    @SuppressLint("SetTextI18n")
    public override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        terraRT = TerraRT(
            DEVID,
            this,
            "refadadas id test"
        ){


            //Generate an SDK token: https://docs.tryterra.co/reference/generate-authentication-token
            //terraRT.initConnection("4a5c2a269d85d38d03a5abb9531955ce3b10a4c723a9055295fde79da0b90c37"){}

        }
        bleConnect = findViewById(R.id.ble)



        bleSwitch = findViewById(R.id.streamBLE)



        bleSwitch.setOnCheckedChangeListener { _, b ->
            if (b){

                GenerateUserToken(XAPIKEY, DEVID, terraRT.getUserId()!!).getAuthToken {
                    terraRT.startRealtime(Connections.BLE, it!!, setOf(DataTypes.HEART_RATE))
                }
            }
            else{
                terraRT.stopRealtime(Connections.BLE)
            }
        }



        bleConnect.setOnClickListener {
            if (bleConnected){
                terraRT.disconnect(Connections.BLE)
                bleConnect.backgroundTintList = ResourcesCompat.getColorStateList(resources, R.color.button_on, null)
                bleConnected = false
            }
            else {
                terraRT.startDeviceScan(Connections.BLE, useCache = false) {
                    if (it) {
                        bleConnect.backgroundTintList = ResourcesCompat.getColorStateList(resources, R.color.button_off, null)
                    }
                }
                bleConnected = true
            }
        }


    }

    public override fun onDestroy() {
        super.onDestroy()
    }

    public override fun onResume(){
        super.onResume()
    }


    companion object{
        const val TAG = "Terra"
        var resource: Connections? = Connections.BLE
    }
}