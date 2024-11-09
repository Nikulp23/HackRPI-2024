import React, { useState } from 'react';
import styles from './../../styles/buttons/FileUpload.module.css'

function FileUpload({ }) {

   const [activeButton, setActiveButton] = useState('imageUpload');

   const handleToggle = (button) => {
      setActiveButton(button);
   };

   return (
      <>
         <div className={styles.container}>
            <div className={`${styles.buttonWrapper} ${styles.buttonWrapperLeft}`}>
               <button className={styles.button} onClick={() => handleToggle('imageUpload')}
                  style={{
                     backgroundColor: activeButton === 'imageUpload' ? 'white' : 'gainsboro'
                  }}>Image Upload</button>
            </div>
            <div className={`${styles.buttonWrapper} ${styles.buttonWrapperRight}`}>
               <button className={styles.button} onClick={() => handleToggle('videoUpload')}
                  style={{
                     backgroundColor: activeButton === 'videoUpload' ? 'white' : 'gainsboro'
                  }}>Video Upload</button>
            </div>
         </div>
      </>
   )
}

export default FileUpload;