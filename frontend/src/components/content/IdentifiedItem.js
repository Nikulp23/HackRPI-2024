import React, { useState } from 'react';
import styles from './../../styles/content/IdentifiedItem.module.css'

function IdenfitiedItem({ facts, infoOnUse, name, use }) {

   return (
      <>
         <div className={styles.subCard}>
            <div className="cardContent">
               <h3 className="cardHeader">{name}</h3>
               <p className="cardSubHeader">{use === "Recycle" ? "These should be recycled!" : "Don't recycle these."}</p>

               <div className={`${styles.howToDispose} ${styles.infoContainer}`}>
                  <div className={styles.info}>
                     <h4 className="cardHeader">How to Dispose:</h4>
                     <p className="cardText">{infoOnUse}</p>
                  </div>
               </div>

               <div className={`${styles.funFacts} ${styles.infoContainer}`}>
                  <div className={styles.info}>
                     <h4 className="cardHeader">Fun Facts:</h4>
                     <p className="cardText">{facts}</p>
                  </div>
               </div>
            </div>
         </div>
      </>
   )
}

export default IdenfitiedItem;