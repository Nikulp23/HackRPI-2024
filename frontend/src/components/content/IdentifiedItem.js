import React, { useState } from 'react';
import styles from './../../styles/content/IdentifiedItem.module.css'
import recycleImg from './../../images/recycle.png';
import reuseImg from './../../images/reuse.png';
import salvageImg from './../../images/firstaid.png'
import uselessImg from './../../images/trash.png'

function IdenfitiedItem({ facts, infoOnUse, name, use }) {

   return (
      <>
         <div className={styles.subCard}>
            <div className="cardContent">
               <div className={styles.itemTitle}>
                  <img src={use === "Recycle" ? recycleImg : use === "Reuse" ? reuseImg : use === "Salvage" ? salvageImg : uselessImg} alt="recycle" />
                  <h3 className="cardHeader">{name}</h3>
               </div>
               <p className="cardSubHeader">{use === "Recycle" ? "These should be recycled!" : use === "Reuse" ? "You can reuse these!" : use === "Salvage" ? "You don't need to throw these away!" : "Don't recycle these."}</p>

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