#inputs 2 list (of equal length - ie. same number of different license types) quantity from community/ies and search engine/ies and returns the estimated total of CC licenses as an integer

def cc_total_estimate(community_list, search_engine_list): 				# Define the function with 2 argument lists the community (Flikr) and the Search Engine
    if len(community_list) == len(search_engine_list): 					# Check if both the list contain quantities for the same number of liceneses
        number_of_lic_types = len(search_engine_list)					# Assign the number of licenses to the "number_of_lic_types" variable
    else: 
        return 0									# If the number doesn't match return 0
    diff_list = []									# Initialize the "Diff_list" variable to store the differnce between the two lists
    count = 0										# Initialize the "count" variable to 0, to help iterate loops
    while count < number_of_lic_types: 							# Loop while "count" less the number of license types
        diff_list.append(search_engine_list[count] - community_list[count])		# Populate the "diff_list" with differences in the values of the 2 argument lists
        count += 1									# Increment "count"
    min_diff = min(diff_list)								# Find and assign minimun of "diff_list" to variable "min_diff"
    min_diff_pos = diff_list.index(min_diff)						# Find and assign index of "min_diff" to variable "min_diff_pos"
    scaling_Factor = 1 - float(min_diff)/float(search_engine_list[min_diff_pos])	# Find the scaling factor of type float and assign it the variable "scaling_factor"
    result = 0										# Initialize variable "result" to 0
    count = 0										# Re-initialize variable "count" to 0
    while count<number_of_lic_types: 							# Loop while "count" less the number of license types
        result += (int(scaling_Factor*search_engine_list[count]))			# Assign result as sum of result and scaling factor multiplied by "search_engine_list" elements
        count += 1									# Increment "count"
    return result									# Return "result"


#inputs 2 list (of equal length - ie. same number of different license types) quantity from community/ies and search engine/ies and returns the estimated total of CC licenses as a list, providing the ability to examine the estimed distribution

def cc_total_estimate(community_list, search_engine_list): 				# Define the function with 2 argument lists the community (Flikr) and the Search Engine
    if len(community_list) == len(search_engine_list): 					# Check if both the list contain quantities for the same number of liceneses
        number_of_lic_types = len(search_engine_list)					# Assign the number of licenses to the "number_of_lic_types" variable
    else: 
        return 0									# If the number doesn't match return 0
    diff_list = []									# Initialize the "Diff_list" variable to store the differnce between the two lists
    count = 0										# Initialize the "count" variable to 0, to help iterate loops
    while count < number_of_lic_types: 							# Loop while "count" less the number of license types
        diff_list.append(search_engine_list[count] - community_list[count])		# Populate the "diff_list" with differences in the values of the 2 argument lists
        count += 1									# Increment "count"
    min_diff = min(diff_list)								# Find and assign minimun of "diff_list" to variable "min_diff"
    min_diff_pos = diff_list.index(min_diff)						# Find and assign index of "min_diff" to variable "min_diff_pos"
    scaling_Factor = 1 - float(min_diff)/float(search_engine_list[min_diff_pos])	# Find the scaling factor of type float and assign it the variable "scaling_factor"
    result = []										# Initialize variable "result" as a list
    count = 0										# Re-initialize variable "count" to 0
    while count<number_of_lic_types: 							# Loop while "count" less the number of license types
        result.append((int(scaling_Factor*search_engine_list[count])))			# Appends to result scaling factor multiplied by "search_engine_list" element
        count += 1									# Increment "count"
    return result									# Return "result"
