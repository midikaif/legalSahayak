import { Alert, Platform, AlertButton, AlertOptions } from "react-native";

export const showAlert = (
  title: string,
  message: string,
  buttons?: AlertButton[],
  options?: AlertOptions,
) => {
  if (Platform.OS === "web") {
    window.alert(`${title}: ${message}`);
  } else {
    setTimeout(() => {
      Alert.alert(title, message, buttons, options);
    }, 500);
  }
};
