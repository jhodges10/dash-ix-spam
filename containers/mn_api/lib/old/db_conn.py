import psycopg2
import psycopg2.extras
import os
import logging
import time
import traceback
from datetime import datetime
from old.settings import DB_DEF


class Database:

    def _init_(self):
        print("Initializing Databse Object")
        logging.info("Initializing Database Object")
        pass

    @staticmethod
    def postgres_db_connection():
        """ 
        Set up the postgres connection for a single connection (more stable on the DB end)
        """
        return psycopg2.connect(**DB_DEF)

    @staticmethod
    def insert_records(insert_statement, values, data_type):
        """
        Inserts a list of values into a database
        param insert_statement: The SQL query used to insert a row of data
        type insert_statement: string representing a SQL query
        param values: the list of tuples to insert into the database
        type values: list containing a tuple
        """
        start_time = time.time()
        if len(values) > 0:
            db = Database.postgres_db_connection()

            cur = db.cursor()
            try:
                if len(values) >= 1:
                    cur.executemany(insert_statement, values)
                    db.commit()
                    if 'INSERT' in insert_statement:
                        print("INSERTED INTO DB")
                    elif 'UPDATE' in insert_statement:
                        print("UPDATED IN DB")
            except Exception as err:
                print("EXCEPTION")
                traceback.print_exc()
                db.rollback()
                print(err)
                pass
            finally:
                cur.close()
                db.close()
        end_time = time.time()
        duration = end_time - start_time
        duration = format(duration, '.2f')

        if 'INSERT' in insert_statement:
            print("Finished inserting {}, took {} seconds".format(data_type, duration))
        elif 'UPDATE' in insert_statement:
            print("Finished updating {}, took {} seconds".format(data_type, duration))

    # Load Data

    @staticmethod
    def get_protx_info():
        """
        Loads a list of values from a database
        param query: The SQL query used to get a row or rows of data
        type query: string representing a SQL query
        """
        query = "SELECT * from protx"
        db = Database.postgres_db_connection()

        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query)
        
        rows = cur.fetchall()
        db.close()

        return rows

    @staticmethod
    def create_tables():
        """
        Create the tables
        """
        query = """create table protx
            (
                protx varchar
                    constraint protx_pk
                        primary key,
                collateralHash varchar,
                collateralIndex varchar,
                collateralAddress varchar,
                operatorReward varchar,
                service varchar,
                registeredHeight bigint,
                lastPaidHeight bigint,
                PoSePenalty integer,
                PoSeRevivedHeight bigint,
                PoSeBanHeight varchar,
                revocationReason varchar,
                ownerAddress varchar,
                votingAddress varchar,
                payoutAddress varchar,
                pubKeyOperator varchar,
                confirmations bigint
            );
        """
        db = Database.postgres_db_connection()

        cur = db.cursor()

        try:
            cur.execute(query)

        except Exception as err:
            print(err)
        db.close()

        return True

    @staticmethod
    def insert_protx_info(protx_list):
        query = """
                INSERT INTO protx (protx, collateralhash, collateralindex, collateraladdress, operatorreward, service, registeredheight, lastpaidheight,
                posepenalty, poserevivedheight, posebanheight, revocationreason, owneraddress, votingaddress,
                payoutaddress, pubkeyoperator, confirmations) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s)
            """
        values_list = []

        for node in protx_list:
            print(node)
            protx = node['proTxHash']
            collateralhash = node['collateralHash']
            collateralindex = node['collateralIndex']
            collateraladdress = node['collateralAddress']
            operatorreward = node['operatorReward']
            service = node['state']['service']
            registeredheight = node['state']['registeredHeight']
            lastpaidheight = node['state']['lastPaidHeight']
            posepenalty = node['state']['PoSePenalty']
            poserevivedheight = node['state']['PoSeRevivedHeight']
            posebanheight = node['state']['PoSeBanHeight']
            revocationreason = node['state']['revocationReason']
            owneraddress = node['state']['ownerAddress']
            votingaddress = node['state']['votingAddress']
            payoutaddress = node['state']['payoutAddress']
            pubkeyoperator = node['state']['pubKeyOperator']
            confirmations = node['confirmations']

            values_tuple = (protx, collateralhash, collateralindex, collateraladdress, operatorreward, service, registeredheight, lastpaidheight,
                        posepenalty, poserevivedheight, posebanheight, revocationreason, owneraddress, votingaddress, payoutaddress, pubkeyoperator, 
                        confirmations)

            values_list.append(values_tuple)

        print("We've got a bunch of data: \n")
        Database.insert_records(query, values_list, "ProTX Info")

if __name__ == "__main__":
    # Database.create_tables()
    Database.get_protx_info()