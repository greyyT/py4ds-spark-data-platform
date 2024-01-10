export const formatTime = (inputTime: string | null) => {
  if (!inputTime) return '';

  const [hour, minute] = inputTime.split(':');

  let formattedTime;

  if (hour === '0') {
    formattedTime = `${minute}m`;
  }

  if (hour !== '0' && minute === '00') {
    formattedTime = `${hour}h`;
  }

  if (hour !== '0' && minute !== '00') {
    formattedTime = `${hour}h ${minute}m`;
  }

  return formattedTime;
};
