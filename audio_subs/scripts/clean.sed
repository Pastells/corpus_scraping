# Neteja de text dels subtítols

# italics and other tags
s/&lt;[^&]*&gt;//g

# color tags
s/^<c\.[^>]*>//g
s/<\/c>//g

# region header
/^Region: id=/d
s/ region: line.*//g

# Remove text within parentheses and the parentheses themselves
s/-*([^()]*)//g

# Remove hypens
s/-\([A-Z#]\)/\1/g

# Remove quotes ""

s/"//g

# Add a space after punctuation marks if followed by a capital letter
s/\([?.!]\)\([A-Z]\)/\1 \2/g

# remove headers
s/CAPÍTOL.*//g
