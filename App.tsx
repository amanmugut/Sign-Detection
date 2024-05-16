import React, { useRef } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { RNCamera } from 'react-native-camera';
import axios from 'axios'; 

const App: React.FC = () => {
    const cameraRef = useRef<RNCamera | null>(null);

    const takePicture = async () => {
        if (cameraRef.current) {
            const options = { quality: 0.5, base64: true };
            const data = await cameraRef.current.takePictureAsync(options);

            const imageBlob = data.uri.startsWith('data:image/jpeg;base64,')
                ? data.uri.split(',')[1]
                : data.uri;

            // Sending the image data to your Python server
            //post requets to server
            try {
                const formData = new FormData();
                formData.append('image', {
                    uri: data.uri,
                    type: 'image/jpeg',
                    name: 'captured_image.jpg',
                });

                //api link
                const response = await axios.post('http://localhost:5000', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
                console.log('Server response:', response.data);
            } catch (error) {
                console.error('Error sending image to server:', error);
            }
        }
    };

    return (
        <View style={styles.container}>
            <RNCamera
                ref={cameraRef}
                style={styles.camera}
                type={RNCamera.Constants.Type.back}
                flashMode={RNCamera.Constants.FlashMode.off}
                androidCameraPermissionOptions={{
                    title: 'Permission to use camera',
                    message: 'We need your permission to use your camera',
                    buttonPositive: 'Okay',
                    buttonNegative: 'Cancel',
                }}
            >
                <View style={styles.overlay}>
                    <TouchableOpacity onPress={takePicture} style={styles.captureButton}>
                        <Text style={styles.captureButtonText}>Capture</Text>
                    </TouchableOpacity>
                </View>
            </RNCamera>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    camera: {
        flex: 1,
        justifyContent: 'flex-end',
        alignItems: 'center',
    },
    overlay: {
        flex: 1,
        flexDirection: 'column',
        justifyContent: 'flex-end',
        alignItems: 'center',
    },
    captureButton: {
        padding: 15,
        backgroundColor: 'white',
        borderRadius: 50,
        marginBottom: 30,
    },
    captureButtonText: {
        fontSize: 16,
        color: 'black',
    },
});

export default App;
