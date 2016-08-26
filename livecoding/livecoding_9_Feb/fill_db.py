import sqlite3

## open connection to sqlite3 db
conn = sqlite3.connect('profile_keywords.db')
c = conn.cursor()


##sql_create_table1 = "CREATE TABLE keywords(profile_name TEXT  NOT NULL,\
##keywords  TEXT  NOT NULL, defaultProfile INT);"

##sql_create_table1 = "insert into keywords(profile_name,\
##keywords  , defaultProfile ) values ('programming', 'aaa,aasas', 1);"
##
##c.execute(sql_create_table1)
##conn.commit()
##
####sql_variables = "CREATE TABLE variables(liveCodingLikeMin INT NOT NULL, liveCodingLikeMax INT NOT NULL,\
####            programmingLanguagesMinLike INT NOT NULL,\
####                 programmingLanguagesMinRT INT NOT NULL, accountFollowedMinLike INT NOT NULL,\
####                 accountFollowedMinRT INT NOT NULL,\
####                 accountFollowedLikeMin INT NOT NULL, accountFollowedLikeMax INT NOT NULL,\
####                 accountFollowedRTMin INT NOT NULL,\
####                 accountFollowedRTMax INT NOT NULL, replyTweet TEXT  NOT NULL, id INT NOT NULL);" 
##
##sql_variables = "insert into variables(liveCodingLikeMin, liveCodingLikeMax ,\
##            programmingLanguagesMinLike ,\
##                 programmingLanguagesMinRT , accountFollowedMinLike ,\
##                 accountFollowedMinRT ,\
##                 accountFollowedLikeMin , accountFollowedLikeMax ,\
##                 accountFollowedRTMin ,\
##                 accountFollowedRTMax , replyTweet , id ) values (1,4,1,20, 1,2,3,4,5,1, 'aass', 0);" 
##
##c.execute(sql_variables)
##conn.commit()

##conn.close()
