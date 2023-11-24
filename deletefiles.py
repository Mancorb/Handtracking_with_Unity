from os import listdir,path,remove

def delete_files_in_directory(directory_path):
   try:
     files = listdir(directory_path)
     for file in files:
       file_path = path.join(directory_path, file)
       if path.isfile(file_path):
        remove(file_path)

   except OSError:
     print("Error occurred while deleting files.")

def delete_it_all():
  directory_path_list = ["A","B","C","D"]
  for letter in directory_path_list:
      delete_files_in_directory("hand_"+letter)
  print("All files deleted successfully.")


  delete_it_all()